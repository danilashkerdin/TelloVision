from cv2 import CascadeClassifier, cvtColor, rectangle, circle, arrowedLine, putText, \
    resize, COLOR_BGR2GRAY, data, line, FONT_HERSHEY_COMPLEX


class FaceVector:
    def __init__(self, height=480, width=640):
        """Arguments: returning image size"""
        self.previous_faces = None
        self.face = None

        self.height = height
        self.width = width
        self.frame_square = self.width * self.height

        """Constants"""

        self.dimensions = [["great", "right", "left"], ["great", "up", "down"], ["great", "forward", "backward"]]

        self.target_face_region_ratio = 0.1
        self.target_square_ratio = 0.05  # face to frame square ratio
        self.delta_square_ratio = self.target_square_ratio * 0.4  # delta face to frame square ratio

        self.img_center = (width // 2, height // 2)
        self.left_upper_corner = (int(self.width * (0.5 - self.target_face_region_ratio)),
                                  int(self.height * (0.5 - self.target_face_region_ratio)))
        self.left_lower_corner = (int(self.width * (0.5 - self.target_face_region_ratio)),
                                  int(self.height * (0.5 + self.target_face_region_ratio)))
        self.right_upper_corner = (int(self.width * (0.5 + self.target_face_region_ratio)),
                                   int(self.height * (0.5 - self.target_face_region_ratio)))
        self.right_lower_corner = (int(self.width * (0.5 + self.target_face_region_ratio)),
                                   int(self.height * (0.5 + self.target_face_region_ratio)))

    @staticmethod
    def sign(n):
        if n > 0:
            return 1
        elif n < 0:
            return -1
        else:
            return 0

    """Face detection"""

    @staticmethod
    def face_detection(image):
        face_cascade = CascadeClassifier(data.haarcascades + 'haarcascade_frontalface_default.xml')
        img_gray = cvtColor(image, COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(image=img_gray)
        return faces

    @staticmethod
    def face_center(face):
        if face is not None:
            (x, y, w, h) = face
            x_center = x + w // 2
            y_center = y + h // 2
            return x_center, y_center
        else:
            return None

    @staticmethod
    def face_square(face):
        if face is not None:
            (_, _, w, h) = face
            return w * h
        else:
            return None

    def face_plotting(self, image, face):
        if face is not None:
            (x, y, w, h) = face
            face_center = self.face_center(face)
            image = rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            image = circle(image, face_center, 10, (0, 255, 0))
            image = arrowedLine(image, face_center, self.img_center, (255, 255, 0))
            return image
        else:
            return None

    """Face and face center definition on image"""

    def face_definition(self, image, face):
        if face is not None:
            image = self.face_plotting(image, face)
        return image

    """Frame processing"""

    def frame_processing(self, image):

        res = circle(image, self.img_center, 10, (0, 0, 255))
        res = line(res, self.left_upper_corner, self.left_lower_corner, (255, 255, 255))
        res = line(res, self.left_upper_corner, self.right_upper_corner, (255, 255, 255))
        res = line(res, self.right_lower_corner, self.right_upper_corner, (255, 255, 255))
        res = line(res, self.right_lower_corner, self.left_lower_corner, (255, 255, 255))
        return res

    def text_addition(self, image, vector_3d):
        if vector_3d is not None:
            putText(image, "Width: " + str(self.dimensions[0][vector_3d[0]]), (0, self.height // 4),
                    FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
            putText(image, "Height:" + str(self.dimensions[1][vector_3d[1]]), (0, 2 * self.height // 4),
                    FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
            putText(image, "Depth:" + str(self.dimensions[2][vector_3d[2]]), (0, 3 * self.height // 4),
                    FONT_HERSHEY_COMPLEX, 1, (255, 255, 255))
        return image

    def direction_vector_3d(self, image):

        image = resize(image, (self.width, self.height))

        faces = self.face_detection(image)

        if faces is not None and len(faces) > 0:
            face = faces[0]
            face_square = self.face_square(face)
            square_ratio = face_square / self.frame_square
            face_center = self.face_center(face)
            result_vector = ((self.img_center[0] - face_center[0]), (self.img_center[1] - face_center[1]))

            direction_vector = [self.sign(int(result_vector[0] / (self.width * self.target_face_region_ratio))),
                                self.sign(int(result_vector[1] / (self.height * self.target_face_region_ratio)))]

            if square_ratio < self.target_square_ratio - self.delta_square_ratio:
                direction_vector.append(1)
            elif square_ratio > self.target_square_ratio + self.delta_square_ratio:
                direction_vector.append(-1)
            else:
                direction_vector.append(0)
            return direction_vector

        else:
            return None

    def direction_vector_3d_with_returning_image(self, image):

        image = resize(image, (self.width, self.height))

        faces = self.face_detection(image)
        image = self.frame_processing(image)

        if faces is not None and len(faces) > 0:
            face = faces[0]

            face_square = self.face_square(face)
            square_ratio = face_square / self.frame_square
            face_center = self.face_center(face)
            result_vector = ((self.img_center[0] - face_center[0]), (self.img_center[1] - face_center[1]))

            direction_vector = [self.sign(int(result_vector[0] / (self.width * self.target_face_region_ratio))),
                                self.sign(int(result_vector[1] / (self.height * self.target_face_region_ratio)))]

            if square_ratio < self.target_square_ratio - self.delta_square_ratio:
                direction_vector.append(1)
            elif square_ratio > self.target_square_ratio + self.delta_square_ratio:
                direction_vector.append(-1)
            else:
                direction_vector.append(0)

            image = self.face_definition(image, face)
            return direction_vector, image

        return None, image

    #
    # """returns (number of pixels to which the center of the face to the left of the center of the image,"""
    # """          number of pixels to which the center of the face is upper than the center of the image)"""
    # def pixel_vector_2d(self, image):
    #
    #     image = resize(image, (self.width, self.height))
    #
    #     faces = self.face_detection(image)
    #     face = None
    #
    #     if faces is not None and len(faces) > 0:
    #         face = faces[0]
    #
    #     face_center = self.face_center(face)
    #
    #     result_vector = None
    #     if face_center is not None:
    #         result_vector = ((self.img_center[0] - face_center[0]), (self.img_center[1] - face_center[1]))
    #     return result_vector
    #
    # """returns (number of pixels to which the center of the face to the left of the center of the image,"""
    # """          number of pixels to which the center of the face is upper than the center of the image)"""
    # def pixel_vector_2d_with_returning_image(self, image):
    #
    #     image = resize(image, (self.width, self.height))
    #
    #     faces = self.face_detection(image)
    #     face = None
    #
    #     if faces is not None and len(faces) > 0:
    #         face = faces[0]
    #
    #     face_center = self.face_center(face)
    #
    #     result_vector = None
    #     if face_center is not None:
    #         result_vector = ((self.img_center[0] - face_center[0]), (self.img_center[1] - face_center[1]))
    #     """Returning vector and image"""
    #     result_image = self.face_definition(image, face)
    #     result_image = self.frame_processing(result_image)
    #     return result_vector, result_image
    #
    # def direction_vector_2d(self, image):
    #     result_vector = self.pixel_vector_2d(image)
    #     direction_vector = None
    #     if result_vector is not None:
    #         direction_vector = (self.sign(int(result_vector[0] / (self.width * self.target_face_region_ratio))),
    #                             self.sign(int(result_vector[1] / (self.height * self.target_face_region_ratio))))
    #     return direction_vector
    #
    # def direction_vector_2d_with_returning_image(self, image):
    #     result_vector, result_image = self.pixel_vector_2d_with_returning_image(image)
    #     direction_vector = None
    #     if result_vector is not None:
    #         direction_vector = (self.sign(int(result_vector[0] / (self.width * self.target_face_region_ratio))),
    #                             self.sign(int(result_vector[1] / (self.height * self.target_face_region_ratio))))
    #     return direction_vector, result_image


def main():
    from cv2 import VideoCapture, imshow, waitKey, flip
    capture = VideoCapture(0)
    resolution = (960, 720)

    fv = FaceVector(resolution[1], resolution[0])
    while True:
        r, i = capture.read()
        if r:
            i = flip(i, 1)
            vec, image = fv.direction_vector_3d_with_returning_image(i)
            image = fv.text_addition(image, vec)
            imshow("", image)
            print(vec)
        if waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
