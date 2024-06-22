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
        image.save(image_path, exif=piexif.dump(self.exif))

    def print_metadata(self):
        exif_data = self.read_metadata()
    
        for ifd_name in exif_data:
            print(f"\n{ifd_name}:")
            if exif_data[ifd_name] is not None:
                for tag in exif_data[ifd_name]:
                    tag_name = piexif.TAGS[ifd_name][tag]["name"]
                    value = exif_data[ifd_name][tag]

                    # Special handling for UserComment
                    if tag_name == "UserComment" and isinstance(value, bytes):
                        value = self.decode_user_comment(value)
                    print(f"    {tag_name}: {value}")

if __name__ == '__main__':
    image_path = input("Please provide an image path")
    adjuster = ImageMetadataAdjuster(image_path)
    adjuster.add_tags("TAG")
    # adjuster.add_subject("test")
    adjuster.save()
    adjuster.print_metadata()
    
