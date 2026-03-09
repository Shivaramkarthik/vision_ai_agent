from vision_processor import process_screen


class VisionAgent:

    def observe(self, image):

        elements = process_screen(image)

        return elements