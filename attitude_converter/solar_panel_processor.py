import traceback
from typing import Tuple, List
from datetime import datetime

import spiceypy as spy
from spiceypy.utils.support_types import SpiceyError
import numpy as np
from .attitude_provider import MappsTimedQuaternion, PanelMex2Ker


class SolarPanelProcessor:

    def __init__(self, probe: str):
        self._probe = probe
        self._m2k = PanelMex2Ker()

    @property
    def probe(self):
        return self._probe

    @staticmethod
    def _create_quaternion(direction: np.ndarray, up: np.ndarray) -> Tuple[float, float, float, float]:
        """ Generates a quaternion described by a direction vector and "upwards" orientation vector.

        https://stackoverflow.com/questions/32208838/rotation-matrix-to-quaternion-equivalence

        :param direction: Direction vector for the quaternion.
        :param up: Upwards direction for the quaternion.
        :return: Desired quaternion (r, i, j, k)
        """
        direction = direction / spy.vnorm(direction)
        up = up / spy.vnorm(up)

        x = np.cross(up, direction)
        x = x / spy.vnorm(x)
        y = np.cross(direction, x)
        y = y / spy.vnorm(y)
        z = direction

        r = np.sqrt(1.0 + x[0] + y[1] + z[2]) * 0.5
        i = (y[2] - z[1]) / (4 * r)
        j = (z[0] - x[2]) / (4 * r)
        k = (x[1] - y[0]) / (4 * r)

        return r, i, j, k

    @staticmethod
    def _find_new_XY_directions(static_Y_vector: np.ndarray, sun_vector: np.ndarray):
        nY = static_Y_vector / spy.vnorm(static_Y_vector)
        nS = sun_vector / spy.vnorm(sun_vector)

        new_Z = nS - (np.dot(nS, nY)) * nY
        new_X = - np.cross(nY, new_Z)

        return new_X, nY

    def _generate_panel_quaternions(self, et_start: float, et_end: float, step_s: float) -> List[MappsTimedQuaternion]:
        """ Generate a list of quaternions that describe the sun-optimized orientation of JUICE's solar panels.

        :param et_start: Start ephemeris time.
        :param et_end: End ephemeris time.
        :param step_s: Sampling step in seconds.
        :return: List of MappsTimedQuaternions for the given period.
        """
        quaternions = []
        ets = np.arange(et_start, et_end, step_s)
        n = len(ets)
        counter_pct = 0
        for i, et in enumerate(ets):
            if 100 * i / n > counter_pct:
                print(f"Progress: {counter_pct} %")
                counter_pct += 10
            JUICE_Y_in_J2000 = spy.spkcpt([0.0, 1.0, 0.0], self.probe, f"{self.probe}_SPACECRAFT", et, "J2000",
                                          "OBSERVER", "NONE", self.probe)[0][0:3]
            JUICE_SUN_in_J2000 = spy.spkpos("SUN", et, "J2000", "LT+S", self.probe)[0]

            new_X, nY = self._find_new_XY_directions(JUICE_Y_in_J2000, JUICE_SUN_in_J2000)

            utc_time_string = spy.et2utc(et, "ISOC", 0) + "Z"
            quaternions.append(MappsTimedQuaternion(utc_time_string, *self._create_quaternion(new_X, nY)))

        return quaternions

    def create_panel_ck(self, start_time: datetime, end_time: datetime, step_s: float, ck_filepath: str):
        start_et = self._datetime2et(start_time)
        end_et = self._datetime2et(end_time)
        try:
            quaternions = self._generate_panel_quaternions(start_et, end_et, step_s)
        except SpiceyError:
            traceback.print_exc()
            raise RuntimeError(f"Quaternion computation for solar panels failed.\nStart time: {start_time}\nEnd time: {end_time}\nCheck console for more details.")
        self._m2k.convert(quaternions, ck_filepath)

    @staticmethod
    def _datetime2et(time: datetime) -> float:
        """ Convert datetime to SPICE ephemeris time."""
        if isinstance(time, float):
            return time
        if not isinstance(time, datetime):
            raise TypeError("Time must be a float or a datetime object.")
        return spy.str2et(time.isoformat())


