# coding: utf-8

import requests
from os import path
from concurrent import futures
from time import sleep
from flask import current_app
from .base import BaseCommand
from ..models import db, page_query, ListMedia

class CheckOldMedia(BaseCommand):

    def __init__(self, logger=None):
        self.logger         = self.get_logger() if logger is None else logger
        self.media_urls     = []
        self.lost_media_ids = []

        self.chekc_old_media_offset_filename = current_app.config.get('CHEKC_OLD_MEDIA_OFFSET_FILENAME')

        self.logger.info("CheckOldMedia")

    def get_offset(self):
        if path.exists(self.chekc_old_media_offset_filename):
            offset = open(self.chekc_old_media_offset_filename).read().strip()

            if len(offset) > 0:
                return offset
            else:
                return None
        else:
            return None

    def write_offset(self, offset_size):
        f = open(self.chekc_old_media_offset_filename, 'w+')
        f.write(str(offset_size))
        f.close()

    def make(self):
        offset_size = self.get_offset()

        if not offset_size:
            self.logger.error("Can not found the offset from file")
        else:
            self.logger.info("---> offset: {0}".format(offset_size))

            list_medias = ListMedia.query.filter(ListMedia.status == "show").order_by(ListMedia.create_at.desc()).offset(offset_size).limit(1000)

            if not list_medias:
                self.logger.info("---> Finished")
                self.write_offset(0)

                return None
            else:
                # Create urls
                self.logger.info("---> Creating medial urls")

                for media in list_medias:
                    self.media_urls.append({
                        'id'  : media.id,
                        'link': media.media_url
                    })

                # Make check action
                self.logger.info("---> Doing check status action")


                with futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_media_url = {
                        executor.submit(self.check, media_url, 60): media_url for media_url in self.media_urls
                    }

                    for future in futures.as_completed(future_to_media_url):
                        media_url = future_to_media_url[future]

                        try:
                            data = future.result()
                        except Exception as exc:
                            self.logger.info('--->---> {0} generated an exception: {1}'.format(media_url['id'], exc))
                        else:
                            self.logger.info('--->---> {0} fetched'.format(media_url['id']))

                # Update media stauts
                self.logger.info("---> Updating media status to lost")

                for media in ListMedia.query.filter(ListMedia.id.in_(self.lost_media_ids)):
                    media.status = "lost"
                    db.session.add(media)

                db.session.commit()

                # Update offset
                self.logger.info("---> Writing offset value to file")
                self.write_offset(int(offset_size) + 1000)

                # Call again
                self.logger.info("---> Enter to next round")

                self.make()

    def check(self, media_url, timeout):
        try:
            r = requests.head(media_url['link'], timeout=timeout)

            if r.status_code != 200:
                self.logger.info("--> [{0}] - {1: >8} - {2}".format(r.status_code, media_url['id'], media_url['link']))
                self.lost_media_ids.append(media_url['id'])
        except:
            self.logger.info("--> [Err] - {0: >8} - {1}".format(media_url['id'], media_url['link']))
            self.lost_media_ids.append(media_url['id'])

        sleep(0.005)
