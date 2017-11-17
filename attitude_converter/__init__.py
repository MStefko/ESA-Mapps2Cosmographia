import os
from attitude_provider import MappsReader, JuiceMex2Ker
   
class AttitudeConverter:
    def convert(self, mapps_attitude_path, output_ck_path):
        bc_reader = MappsReader()
        bc_reader.read(mapps_attitude_path)
        quats = bc_reader.quaternions
        bc2ck = JuiceMex2Ker()
        bc2ck.convert(quats, output_ck_path)