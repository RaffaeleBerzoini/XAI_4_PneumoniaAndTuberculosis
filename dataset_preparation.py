import os
import shutil
import zipfile


def extract_dataset(zipped_dataset, output_directory):
    """
        Extracts the dataset from the zipped file and moves the folders to the root directory.
        :param zipped_dataset The path to the zipped dataset.
        :param output_directory: The path to the output directory.
        :return: None
    """

    shutil.rmtree(output_directory, ignore_errors=True)
    os.makedirs(output_directory, exist_ok=True)
    with zipfile.ZipFile(zipped_dataset, 'r') as zip_ref:
        zip_ref.extractall(output_directory)

    path_to_data = output_directory + 'train'
    for folder in os.listdir(path_to_data):
        shutil.rmtree(os.path.join(output_directory, folder), ignore_errors=True)
        shutil.move(os.path.join(path_to_data, folder), output_directory)
    os.rmdir(path_to_data)


if __name__ == '__main__':
    extract_dataset('train_set.zip', 'dataset/')
