from dataset_utils import *
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, KernelPCA
import numpy as np
import matplotlib.pyplot as plt
import cv2
import seaborn as sns

LABELS = ["NORMAL", "PNEUMONIA", "TUBERCULOSIS"]


def get_x(datagen):
    x = []
    # y_train0= []
    for index in range(datagen.__len__()):
        img, lbl = datagen.__getitem__(index)
        x.append(img)
        # y_train0.append(lbl)
    X = np.concatenate(x)
    return np.squeeze(X, axis=-1)


if __name__ == '__main__':
    seed = 1
    classes = 3
    batch_size = 32

    patients = make_list_of_patients()

    patients_train, patients_test = test_split(data=patients)
    X_train_folds, y_train_folds, X_val_folds, y_val_folds = stratified_cross_validation_splits(data=patients_train)
    X_test, y_test = dataframe2lists(patients_test)

    x_train_fold0 = X_train_folds[0]
    y_train_fold0 = y_train_folds[0]

    x_val_fold0 = X_val_folds[0]
    y_val_fold0 = y_val_folds[0]

    dg_train0 = DataGen(batch_size, (256, 256), x_train_fold0, y_train_fold0)
    dg_val0 = DataGen(batch_size, (256, 256), x_val_fold0, y_val_fold0)

    x_train0 = get_x(dg_train0)
    x_val0 = get_x(dg_val0)
    num_img = 20
    x_train0 = x_train0[:num_img]
    x_val0 = x_val0[:num_img]

    x_train0_reshaped = x_train0.reshape(len(x_train0), 256 * 256)
    x_val0_reshaped = x_val0.reshape(len(x_val0), 256 * 256)

    # PCA
    pca = PCA()  # linear pca
    kernel_PCA = KernelPCA(kernel="poly", gamma=1e-3, fit_inverse_transform=True, alpha=5e-3)

    pca.fit(x_train0_reshaped)
    _ = kernel_PCA.fit(x_train0_reshaped)

    x_reconstructed_kernel = kernel_PCA.inverse_transform(kernel_PCA.transform(x_val0_reshaped))
    x_reconstructed_pca = pca.inverse_transform(pca.transform(x_val0_reshaped))

    x_reconstructed_kernel = x_reconstructed_kernel.reshape(x_val0.shape)
    x_reconstructed_pca = x_reconstructed_pca.reshape(x_val0.shape)

    for i in range(5):
        fig, axs = plt.subplots(1, 3, constrained_layout=True)
        axs[0].imshow(x_val0[i], cmap="gray")
        axs[0].set_title("Original " + str(i))
        axs[1].imshow(x_reconstructed_kernel[i], cmap="gray")
        axs[1].set_title("Poly Kernel " + str(i))
        axs[2].imshow(x_reconstructed_pca[i], cmap="gray")
        axs[2].set_title("PCA reconstructed " + str(i))
        plt.show()

    # DATA EXPLORATION
    group_train = pd.DataFrame(list(zip(dg_train0.input_img_paths, dg_train0.target)),
                               columns=['count', 'label'])
    group_val = pd.DataFrame(list(zip(dg_val0.input_img_paths, dg_val0.target)),
                             columns=['count', 'label'])
    label_group_t = group_train[['count', 'label']].groupby(['label']).count().reset_index()
    label_group_t['dataset'] = 'training'
    label_group_v = group_val[['count', 'label']].groupby(['label']).count().reset_index()
    label_group_v['dataset'] = 'validation'
    label_group = pd.merge(left=label_group_t, right=label_group_v, how='outer')
    sns.barplot(x='label', y='count', hue='dataset', data=label_group)
    title = "Number of images per class"
    plt.title(title)
    plt.show()

    image_indexes = [1, 12, 18, 19, 124]
    start_pointx = 0
    end_pointx = 25
    start_pointy = 231
    end_pointy = 256
    i = 0
    images, labels = get_images(image_indexes)
    for img, label in zip(images, labels):
        image = img[0, :, :, 0]

        # select ROI
        roi = image[start_pointy:end_pointy, start_pointx:end_pointx]
        plt.imshow(roi / 255, cmap='gray')
        titleroi = "ROI of images:" + str(image_indexes[i])
        plt.title(titleroi)

        fig, axs = plt.subplots(nrows=1, ncols=2)
        label = label[0]
        image_rect = cv2.rectangle(image, (start_pointx, start_pointy), (end_pointx, end_pointy), 2)

        axs[0].imshow(image_rect, cmap='gray')

        axs[1].hist(roi.ravel(), 256, [0, 256])
        title = "Label: " + LABELS[np.argmax(label)] + "\n Image: " + str(image_indexes[i])
        plt.suptitle(title)

        plt.show()
        i = i + 1