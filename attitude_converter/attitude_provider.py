from __future__ import print_function
import re
import os
from subprocess import call
from attitude_converter.time_utils import MappsTime
from sys import platform as _platform
import shutil


class MappsTimedQuaternion:

    def __init__(self, utc_time, value, axis1, axis2, axis3):

        self.time = MappsTime(utc_time)
        self.value = float(value)
        self.axis1 = float(axis1)
        self.axis2 = float(axis2)
        self.axis3 = float(axis3)

    def get_time(self):
        return self.time.tdb_str()

    def get_moc_format(self):
        return '%s %f %f %f %f' % (self.get_time(), self.axis1, self.axis2, self.axis3, self.value)


class MappsReader:

    EXPECTED_MSG = "Expected format<br>{julian-date}{doy-date}{utc-date}{q-value}{q-axis-1}{q-axis-2}{q-axis-3}"

    def __init__(self):
        self.quaternions = []
        self.errors = []

    def read(self, filename):
        with open(filename) as qmapps:
            nlines = 0
            for line in qmapps:
                quatMatch = re.match('(\d+).*', line)
                if quatMatch:
                    fields = line.split(',')
                    try:
                        tq = MappsTimedQuaternion(fields[2], fields[3], fields[4], fields[5], fields[6])
                        self.quaternions.append(tq)
                    except:
                        raise ValueError('Error processing %s (ln: %d)<br><br>%s' %
                                         (os.path.basename(str(filename)),
                                         nlines, MappsReader.EXPECTED_MSG))

                nlines += 1
            print("  Lines read: {}".format(nlines))


class MocExporter:

    BLOCK_SIZE = 500000

    def __init__(self, quaternions, leapsecond, sclk, object_name, object_id):
        self.quaternions = quaternions
        self.leapsecond = leapsecond
        self.sclk = sclk
        self.object_name = object_name
        self.object_id = object_id
        self.creation_date = '2016-10-07T17:00:00'

    def export_moc_header(self):
        return 'ESOC_TOS_GFI_ATTITUDE_FILE_VERSION = 1.0' + os.linesep

    def export_moc_block(self, quaternion_list):

        block_st = quaternion_list[0].get_time()
        block_et = quaternion_list[-1].get_time()

        block = os.linesep + 'META_START' + os.linesep
        block += ('OBJECT_NAME          = %s' + os.linesep) % self.object_name
        block += ('OBJECT_ID            = %d' + os.linesep) % self.object_id
        block += 'REF_FRAME            = EME2000' + os.linesep
        block += 'TIME_SYSTEM          = TDB' + os.linesep
        block += ('START_TIME           = %s' + os.linesep) % block_st
        block += ('STOP_TIME            = %s' + os.linesep) % block_et
        block += ('CREATION_DATE        = %s' + os.linesep) % self.creation_date
        block += 'FILE_TYPE            = ATTITUDE FILE' + os.linesep
        block += 'VARIABLES_NUMBER     = 4' + os.linesep
        block += 'DERIVATIVES_FLAG     = 0' + os.linesep
        block += 'META_STOP' + os.linesep

        for tquat in quaternion_list:
            block += ("%s" + os.linesep) % (tquat.get_moc_format())

        return block

    def export_moc(self, fd):
        fd.write(self.export_moc_header())
        total = len(self.quaternions)
        for i in range(0, total, MocExporter.BLOCK_SIZE):
            block = self.export_moc_block(self.quaternions[i:min(i + MocExporter.BLOCK_SIZE, total)])
            fd.write(block)

    def export_setup(self, fd):
        fd.write("\\begindata\n")
        fd.write(("LEAPSECONDS_FILE     = '%s'" + os.linesep) % self.leapsecond)
        fd.write(("SCLK_KERNEL          = '%s'" + os.linesep) % self.sclk)
        fd.write("INTERPOLATION_DEGREE = 9" + os.linesep)
        fd.write("INTERPOLATION_METHOD = 'LAGRANGE'" + os.linesep)
        fd.write("NOMINAL_SCLK_RATE    = 0.152587890625D-4" + os.linesep)
        fd.write("APPEND_TO_OUTPUT     = 'NO'" + os.linesep)
        fd.write(("STRING_MAPPING       = ( 'EME2000', 'J2000', '%s', '%s'  )" + os.linesep) %
                 (self.object_name, self.object_name))
        fd.write(("NAIF_BODY_NAME       = '%s'" + os.linesep) % self.object_name)
        fd.write(("NAIF_BODY_CODE       = -%d000" + os.linesep) % self.object_id)
        fd.write("\\begintext" + os.linesep)


class Mex2Ker:

    def __init__(self, tls_path, tsc_path, object_name, object_id):
        self.tls_path = tls_path
        self.tsc_path = tsc_path
        self.object_name = object_name
        self.object_id = object_id

    def convert(self, quaternions, ck_path):
        # if the output path contains a space, Mex2Ker will fail. instead we output the
        # file into current folder, and then move it into desired folder
        if " " in ck_path:
            output_ck_path = "temp_ck_file.ck"
            print("Space in output CK path. Creating temporary file: {}".format(output_ck_path))
        else:
            output_ck_path = ck_path

        moc_exp = MocExporter(quaternions, self.tls_path, self.tsc_path, self.object_name, self.object_id)

        working_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

        moc_path = os.path.join(working_path, 'quaternion.moc')
        with open(moc_path, 'wb') as moc_file:
            moc_exp.export_moc(moc_file)

        setup_path = os.path.join(working_path, 'quaternion.setup')
        with open(setup_path, 'wb') as setup_file:
            moc_exp.export_setup(setup_file)

        try:
            os.remove(output_ck_path)
        except OSError:
            print ('pass')
        original_cwd = os.getcwd()
        os.chdir(working_path)

        if _platform == "win32":
            # Windows
            return_val = call(['./mex2ker_win_32bit',
                               '-input', 'quaternion.moc',
                               '-setup', 'quaternion.setup',
                               '-output', output_ck_path])
            if return_val:
                raise RuntimeError("Mex2Ker returned error value: {}".format(return_val))
        else:
            raise RuntimeError("Unsupported platform.")

        # if we had a space, we move the output ck into the desired location
        if " " in ck_path:
            print('Moving file "{}" to "{}"'.format(output_ck_path, ck_path))
            shutil.move(output_ck_path, ck_path)
        os.chdir(original_cwd)


class JuiceMex2Ker(Mex2Ker):

    def __init__(self):

        tls_path = 'naif0011.tls'
        tsc_path = 'juice_fict_20160326.tsc'

        if _platform == "win32":
            tls_path = 'naif0011.tls.win'
            tsc_path = 'juice_fict_20160326.tsc.win'

        object_name = 'JUICE'
        object_id = 28
        Mex2Ker.__init__(self, tls_path, tsc_path, object_name, object_id)


