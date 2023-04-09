# Predicting-Grades and behaviour with semi supervised learning with-Regression-Models as well as ensemble models for streaming data

Description: This section contains two different implementations of regression
models for predicting student grades. The first model is a neural network,
while the second model is a semi-supervised algorithm and the final one is 
implementation of ensemble models which can overcome the issues prevailing over 
streaming data.

The neural network model is built using TensorFlow, a popular open-source machine
learning library. It takes as input various features related to student performance,
such as previous grades, attendance, and study habits. The model is trained using
a large dataset of student records, and then tested on a held-out set of data to
evaluate its accuracy. The code includes detailed comments to help users understand
the structure and operation of the model.

The second model is a semi-supervised algorithm that uses both labeled and unlabeled
data to make predictions. It leverages the fact that some student data may be missing
or incomplete, and uses clustering techniques to group similar students together. It
then assigns labels to these groups based on the known final grades of some students,
and uses this information to make predictions for the remaining students. The code
includes several helper functions and visualization tools to help users explore the
data and understand the algorithm's output and atlast an ensemble model has been used
to overcome the cons of streaming data which has overcome the average performance of
all the models used.

Both models are designed to be flexible and easy to use, with options for adjusting
hyperparameters and input data. They can be run locally or in a cloud environment
using popular platforms such as Google Colab. The code is fully documented and
available under an open-source license, allowing other researchers and developers
to build on this work and contribute to the field of student performance prediction
and the fututre works can be attributed towards the implentation of full fledged online 
learning performance prediction as well as proctoring system.




