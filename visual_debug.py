import cv2


def draw_debug(image, elements):

    debug_img = image.copy()

    for e in elements:

        x1 = e["x1"]
        y1 = e["y1"]
        x2 = e["x2"]
        y2 = e["y2"]

        label = f'{e["type"]} {e["text"]}'

        # Draw box
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw label
        cv2.putText(
            debug_img,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

        # Draw center click point
        cv2.circle(debug_img, (e["x"], e["y"]), 4, (0, 0, 255), -1)

    cv2.imshow("AI Vision Debug", debug_img)

    cv2.waitKey(1)