from attitude_converter.attitude_provider import MappsReader, JuiceMex2Ker


def convert(mapps_attitude_path: str, output_ck_path: str) -> None:
    """
    :param mapps_attitude_path: Path to attitude .csv file containing Quaternions.
    :param output_ck_path: Path to output file to be created by Mex2Ker.
    """
    print(" Reading MAPPS attitude file: {}".format(mapps_attitude_path))
    bc_reader = MappsReader()
    bc_reader.read(mapps_attitude_path)
    quats = bc_reader.quaternions
    print(" Running Mex2Ker.")
    bc2ck = JuiceMex2Ker()
    bc2ck.convert(quats, output_ck_path)
