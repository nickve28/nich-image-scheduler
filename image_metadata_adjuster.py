import piexif
from PIL import Image

class ImageMetadataAdjuster:
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = None
        self.exif = None

    def get_image(self) -> Image:
        if not self.image:
            self.image = Image.open(self.image_path)
        return self.image
    
    def decode_user_comment(self, comment_bytes):
        # for now this is ok, all our content is utf-8
        return comment_bytes.decode('utf-8')

    def read_metadata(self) -> hash:
        image = self.get_image()
        if not self.exif:
            self.exif = piexif.load(image.info['exif'])
        return self.exif
    
    def get_caption(self) -> str:
        exif = self.read_metadata()
        if piexif.ImageIFD.XPSubject not in exif['0th']:
            return ""
        caption = exif['0th'][piexif.ImageIFD.XPSubject]
        if isinstance(caption, tuple):
          caption = ''.join(chr(x) for x in caption[::2])
        return caption     
    
    def add_tags(self, tags):
        exif = self.read_metadata()

        if piexif.ImageIFD.XPKeywords not in exif['0th']:
            exif['0th'][piexif.ImageIFD.XPKeywords] = ''
  
        current_keywords = exif['0th'][piexif.ImageIFD.XPKeywords]
        if isinstance(current_keywords, tuple):
          current_keywords = ''.join(chr(x) for x in current_keywords[::2])
        
        merged_keywords = current_keywords
        if merged_keywords != '':
            merged_keywords += ';'
        merged_keywords += tags
        # todo why utf16 here?
        exif['0th'][piexif.ImageIFD.XPKeywords] = merged_keywords.encode('utf-16le')
        self.exif = exif

    def add_subject(self, subject):
        exif = self.read_metadata()

        exif['0th'][piexif.ImageIFD.XPSubject] = subject.encode('utf-16le')
        self.exif = exif

    def save(self):
        image = self.image
        image.save(self.image_path, exif=piexif.dump(self.exif))
