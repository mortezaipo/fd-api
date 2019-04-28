"""Face-Detection API.

License: GPL-3.0
"""
from typing import Union, Any
from uuid import uuid4
import urllib.request

import tornado.ioloop
from tornado.escape import json_decode, json_encode
import tornado.web
import tornado.log
import face_recognition
import setting


def parse_request(body: str) -> Union[dict, bool]:
    """Validate request body."""
    if not body:
        return False

    parsed_body = {}
    try:
        parsed_body = json_decode(body)
    except Exception:
        return parsed_body

    if "image_url" not in parsed_body:
        return False

    if not parsed_body["image_url"] or not isinstance(parsed_body["image_url"], str):
        return False

    return parsed_body


class FaceDetectionHandler(tornado.web.RequestHandler):
    """Face-Detection implementation class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__url_obj = urllib.request.URLopener()

    def _render(self, is_error: bool, data: Any) -> None:
        """Prepare rendered response."""
        response = {"is_error": is_error, "data": data}
        self.write(json_encode(response))

    def _download_file(self, http_path: str) -> str:
        """Download file and put it in local temp storage."""
        temp_file_path = str(setting.TEMP_DIR.joinpath(uuid4().hex))
        try:
            self.__url_obj.retrieve(http_path, temp_file_path)
        except Exception as e:
            tornado.log.app_log.error("downloading and storing the file failed, %s", e)
            return ""
        return temp_file_path

    def post(self) -> None:
        """Post request handler."""
        # validate input
        request = parse_request(self.request.body)
        if not request:
            return self._render(True, "invalid input")

        # download the picture
        downloaded_file_path = setting.TEMP_DIR.joinpath(self._download_file(request["image_url"]))
        if not downloaded_file_path.name:
            return self._render(True, "Could not download the picture")

        # detect faces
        face_picture = face_recognition.load_image_file(str(downloaded_file_path))
        face_locations = face_recognition.face_locations(face_picture)

        # remove downloaded picture
        downloaded_file_path.unlink()

        return self._render(False, [len(face_locations)])


def main():
    return tornado.web.Application([
        (r"/v1/face-detection/", FaceDetectionHandler)
    ])


if __name__ == "__main__":
    app = main()
    app.listen(8282)
    tornado.ioloop.IOLoop.current().start()
