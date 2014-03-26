import os
import shutil
import sys
import pickle

from PIL import Image


#Based on http://blog.safariflow.com/2013/11/26/image-hashing-with-python/
def average_hash(image):
    """ Returns the average hash of the image. """

    image = image.resize((16, 16), Image.ANTIALIAS)
    image = image.convert('L')

    pixels = list(image.getdata())
    average = sum(pixels) / len(pixels)

    bits = "".join(map(lambda pixel: '1' if pixel < average else '0', pixels))

    return bits


# Taken from: http://en.wikipedia.org/wiki/Hamming_distance
def hamming_distance(s1, s2):
    """ Return the Hamming distance between equal-length sequences. """

    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


def find_identical_hash(current_hash, hash_index, similarity_threshold=95):
    """ Search through the hash_index looking for an entry with a similarity greater than the threshold. """

    for image_path, image_hash in hash_index.iteritems():

        dist = hamming_distance(current_hash, image_hash)
        similarity = (256 - dist) * 100 / 256

        if similarity > similarity_threshold:

            return image_hash

    return None


def move_to_folder(source_folder, new_folder_name, image_to_move):
    """ Used to move a file to a specified folder. """

    if not os.path.isdir(source_folder):
        raise RuntimeError(" Source folder specified to move image is invalid. ")

    new_folder = os.path.join(source_folder, new_folder_name)

    if not os.path.isdir(new_folder):
        os.makedirs(new_folder)

    try:
        shutil.move(image_to_move, new_folder)
    except shutil.Error:
        os.remove(image_to_move)
        pass


def clean_index(index, source_folder):
    """ Used to validate that all entries in the index are still referencing to existing images in the directory.
        We assume that the hash associated with an existing image is still valid. """

    for file_path in index.keys():
        if not os.path.isfile(file_path):
            del index[file_path]

    return index


def get_index_location(source_folder):
    """ Return the supposed location of the index file based on its supposed source folder. """
    return os.path.join(source_folder, '_images_index.pickle')


def get_hash_index(source_folder):
    """ Used to obtain the current index of image hashes for the directory if it exists. """

    # Default to an empty dictionary
    images_hash_index = {}

    # Try to open existing index
    index_file_location = get_index_location(source_folder)
    try:
        with open(index_file_location, 'rb') as handle:
            images_hash_index = pickle.load(handle)
    except IOError:
        pass

    images_hash_index = clean_index(images_hash_index, source_folder)

    return images_hash_index


def save_hash_index(source_folder, index):
    """ Used to save the index. """

    index_file_location = get_index_location(source_folder)

    with open(index_file_location, 'wb') as handle:
        pickle.dump(index, handle)


def remove_duplicate_images(target_folder, expected_size=None):
    """ Main function used to remove duplicate images from a folder. """

    if not os.path.isdir(target_folder):
        raise RuntimeError(" Folder specified for duplicate removal is invalid.")

    file_names = os.listdir(target_folder)

    images_hash_index = get_hash_index(target_folder)

    error_count = 0
    duplicate_count = 0
    resolution_move_count = 0

    # For each file
    for file_name in file_names:

        file_path = os.path.join(target_folder, file_name)

        # Skip already indexed files
        if file_path in images_hash_index.keys():
            continue

        # Try to open image, will fail if not an image.
        try:
            image_fp = open(file_path, "rb")
            image = Image.open(image_fp)
        except IOError:
            # Not an image
            continue

        # Try to load the image, will fail if image is invalid.
        try:
            image.load()
        except IOError:
            # Image is not valid!
            image_fp.close()
            error_count += 1
            move_to_folder(target_folder, 'Errors', file_path)
            continue

        # We can now close the image file
        image_fp.close()

        # Check if the image is of the expected resolution
        if expected_size is not None and (image.size[0] != expected_size[0] or image.size[1] != expected_size[1]):
            move_to_folder_name = "{width}x{height}".format(width=image.size[0], height=image.size[1])
            move_to_folder(target_folder, move_to_folder_name, file_path)
            resolution_move_count += 1
            continue

        image_hash = average_hash(image)

        # Search for an image with an equivalent hash in the index
        if find_identical_hash(image_hash, images_hash_index) is not None:
            move_to_folder(target_folder, 'Duplicates', file_path)
            duplicate_count += 1
            continue
        else:
            images_hash_index[file_path] = image_hash

        save_hash_index(target_folder, images_hash_index)

    print("Duplication removal: {0} duplicates, {1} unexpected resolution, {2} invalid images".format(
        duplicate_count, resolution_move_count, error_count))


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of arguments. Usage: python bing_image_downloader.py destination_folder")
        quit()

    path = sys.argv[1]

    if not os.path.isdir(path):
        print("Specified destination is not a valid folder.")
        quit()

    remove_duplicate_images(path)