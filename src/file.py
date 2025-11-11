
from models import FileTable

def get_file(path, with_add=True):
    """ファイルpathからFileオブジェクトを取得。なければ作成

    Args:
        path (str): ファイルパス
        with_add (bool, optional): なかった場合作成するかどうか. Defaults to True.
    Returns:
        (File, int): ファイルオブジェクトとそのID
    """
    file_obj = FileTable.get(path)
    if not file_obj and with_add:
        file_obj = FileTable.create(path)
    return file_obj, file_obj.id if file_obj else None