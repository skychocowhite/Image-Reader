import os
import pathlib


class AssetHandler():
    asset_path = str(pathlib.Path(
        __file__).parent.absolute()) + '/../_assets_/'
