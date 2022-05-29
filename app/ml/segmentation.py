import torch
import numpy as np

from .utils.segmentation import get_model, get_preprocessing


model = get_model()
preprocessing = get_preprocessing()


def segment_walruses(img: np.array, device='cpu') -> np.array:
    """ Сегментация моржей с помощью модели resnet18 + unet
    Разбиваем на участки 384, 480 и для каждого производим сегментацию.
    """
    image = preprocessing(image=img)['image']

    output_mask = np.zeros(image.shape[1:])

    for x_end in range(480, img.shape[1] + 480, 480):
        for y_end in range(384, img.shape[0] + 384, 384):
            y_end = min(y_end, img.shape[0])
            x_end = min(x_end, img.shape[1])

            image_part = image[:, y_end - 384:y_end, x_end - 480:x_end]

            x_tensor = torch.from_numpy(image_part).type(torch.FloatTensor).to(device).unsqueeze(0)
            pr_mask = model.predict(x_tensor)
            pr_mask = pr_mask.squeeze().round().detach().cpu().numpy()

            output_mask[y_end - 384:y_end, x_end - 480:x_end] = pr_mask

    return output_mask
