""" Implementation of facial recognition using eigenfaces (Algorithm 1).

This module imports a set of images and processes them, so
that they can be used for facial recognition.

It also implements the function `recognize_face`, used to
implement and test the eigenfaces method.

Link to AT&T dataset: https://www.kaggle.com/kasikrit/att-database-of-faces
"""
#%% Import libraries

from PIL import Image as img
import matplotlib.pyplot as plt
import numpy as np
import os

### Constants

# Directory where training images are
source_directory = "./att-database/jpg-images/"

image_dimensions = (112, 92)

# Compute size of image when rearrenged into vector
image_size = image_dimensions[0]*image_dimensions[1]

# Number of selected images per subject
imgs_per_subject = 9

### Prepare data to be used for facial recognition

# Compute the matrix whose columns are the images
# rearrenged into vectors.

face_matrix = np.empty((image_size, 0))
# It's important that the columns of the matrix
# are organized. Columns 0-8 belong to subject 1,
# 9-17 to subject 2 and so forth.
for i in range(1, 41):
    subject = "s" + str(i)
    # Expression used to select a subset of subjects
    selected_subjects = not "40" in subject
    if selected_subjects:
        for image in os.listdir(source_directory + subject):
            # Expression used to select a subset of faces for a given subject
            selected_faces = not "_2" in image
            if selected_faces:
                file_name = source_directory + subject + "/" + image
                with img.open(file_name) as face_image:
                    face_vector = np.array(face_image).reshape((image_size, 1))
                    face_vector = face_vector/255 # work with entries from 0 to 1
                    face_matrix = np.hstack((face_matrix, face_vector))

# Compute average face
average_face = np.mean(face_matrix, axis=1).reshape((image_size, 1))

# Subtract average face from matrix of faces
data = face_matrix - average_face

# Compute the data's SVD (U and V are not square)
u, Sigma, vt = np.linalg.svd(data, full_matrices=False)

#%% Function definition (implementation of facial recognition)

def recognize_face(eigen_num: int, subj_img: tuple,
                   proj_err_limit=2500.00, coeff_err_limit=10.0):
    """Uses the eigenfaces method to recognize an image.

    This function uses the eigenfaces method, along with the first
    classification algorithm described in the report, to recognize
    faces.

    The result of the recognition is printed on the screen, along
    with the projection error and the distance from the reconized person.
    If a known subject has been sucessfully recognized, its number will
    be printed, along with the number of the subject given as a parameter.
    The recognized subject's face will pop up.

    Parameters
    ----------

    eigen_num : int
        Number of eigenfaces to be used for recognition.
    subj_img : tuple of int
        Specification of the image to be recognized.
        The first entry of the tuple is the subject's number
        (between 1 and 40, inclusive) and the second entry,
        the number of the subject's photo (between 1 and 10,
        inclusive).
    proj_err_limit : float
        Threshold for projection error. Consulted to see if image
        is a face or not. Denoted by theta_{delta} on the report.
    coeff_err_limit : float
        Threshold for distance between projections. Consulted to see
        if a face image belongs to any known individual. Denoted by
        theta_{epsilon} on the report.
    """
    # Matrix of eigenfaces (useful for projections)
    eigenfaces = u[:, :eigen_num]

    # Convert face to be recognised into an array
    subject = subj_img[0]
    image = subj_img[1]
    subject_image = "s"+str(subject)+"/s"+str(subject)+"_"+str(image)+".jpg"
    unknown_face = np.array(img.open(source_directory + subject_image)).reshape((image_size, 1))
    unknown_face = unknown_face/255 # work with entries from 0 to 1
    unknown_face = unknown_face - average_face

    # Project the unknown face onto the space generated by the
    # eigenfaces (the face space). Store the coefficients that
    # are used to generate this projection using the basis of 
    # eigenvectors.
    unknown_face_coeff = []
    for i in range(len(eigenfaces[0, :])):
        coeff = np.dot(eigenfaces[:, i], unknown_face)
        unknown_face_coeff.append(coeff[0])
    unknown_face_coeff = np.array(unknown_face_coeff)

    # Compute, in the canonical base, the projection of the
    # uknown face onto the face space
    projection = eigenfaces @ unknown_face_coeff

    projection_error = np.linalg.norm(unknown_face - projection)

    # return projection_error

    # Check if unknown image is a face
    if projection_error > proj_err_limit:
        print("Projection error:", projection_error)
        print("Not a face.")
    else:
        # Compute coefficiets of the projection of the
        # known faces onto the face space
        known_faces_coeff = eigenfaces.T @ data

        # Compute the norm of the difference between the
        # coefficients that generate the unknown face and
        # the coefficients that generate each of the known
        # faces
        difference = []
        for i in range(len(data[0, :])):
            diff_norm = np.linalg.norm(known_faces_coeff[:, i] - unknown_face_coeff)
            difference.append(diff_norm)
        difference = np.array(difference)

        # Group differences by subject (one in each line)
        num_groups = len(difference)//imgs_per_subject
        difference = difference.reshape(num_groups, imgs_per_subject)

        # Compute mean of differences per subject
        difference_mean = difference.mean(axis=1)

        # Take the minimum of those differences
        face_error = difference_mean.min()

        # Check if the face is unknown
        if face_error > coeff_err_limit:
            print("Projection error:", projection_error)
            print("Distance from matched person:", face_error)
            print("Unknown face.")
        else:
            print("Projection error:", projection_error)
            print("Distance from matched person:", face_error)
            print("There's a match!")
            # Take the index of difference minimum, to rebuild
            # the matched face.
            match = np.argmin(difference_mean)
            if (match + 1) == subject:
                print("Got it right.")
            else:
                print("Got it wrong.")
            print("Match:", match+1)
            print("subject:", subject)
            print(match+1 == subject)

            # Convert to data's index
            match *= imgs_per_subject

            # Rebuild matched face and show it
            match_face_array = face_matrix[:, match].reshape(image_dimensions)
            plt.imshow(match_face_array, cmap="gray")
            plt.show()

### Examples:

recognize_face(33, (3, 4))
recognize_face(33, (1, 2))
recognize_face(33, (10, 2))

## Save eigenfaces (uncomment this part if desired)
## Directory to output eigenfaces, if necessary
# eigen_directory = "./att-database/eigenfaces/"
# average_face = average_face.reshape((1, image_size))
# for i in range(345, 349): # select range of eigenfaces to save
#     eigenface = u[:, i]
#     matrix = eigenface.reshape(image_dimensions)
#     plt.imshow(matrix, cmap="gray")
#     plt.axis("off")
#     plt.savefig(eigen_directory + "eigenface" + str(i+1) + ".jpg")