# Deep Learning Retraining on a Tumblr Blog

This is a small sample on how one can retrain the top layer of a model with unorthodox data. There are two parts of this project:
 1. A way to extract image information from Tumblr. A large number of blogs on Tumblr with plenty of tagged images. If these tags are used as labels, one could make a model that predicts how an image will be classified.
 2. Adjustments to the tensorflow object detection training script to use prelabeled data.

# Motive

So why would I spend time to do this?
1. I've been playing around with retraining Inception for a while, so wanted to use those skills in a new context.
2. This a small test of my ability to grab data from an unorthodox source and apply it to a deep learning context. This is an essential skill given how important one's data is for training.

# Part 1: Collecting Data
A major step is collecting appropriate data. A possible untapped resource is tumblr, where people tag their posts all of the time. Therefore I made a script that can allow you to download all of the pictures with a specific tag. While this shouldn't be used for commercial purposes it can help with creating a large, sorted image set fast.

This was made as a quick way for me to download all of the appropriate images from a blog I curate (artcive.tumblr.com). I'll update this code to be more flexible if there is demand for it, but otherwise I'll focus on the TensorFlow portion of this project.

# Part 2: Training Model
Firstly thank you Dat Tran for your invaluable [blog post](https://towardsdatascience.com/how-to-train-your-own-object-detector-with-tensorflows-object-detector-api-bec72ecfe1d9) on how to retrain a model in TensorFlow's object detection library, it (along with the offical documentation) was invaluable in seeing how to go about this. The steps below will show how one can use this repo to speed up your training process.

## Setup
1. [Installing Tensorflow](https://www.tensorflow.org/install/install_windows). I was able to get through 160 steps on a gaming laptop in 24 hours with the CPU support only, so it isn't terrible if you download the CPU portion. Just as a heads up though the load is enough to almost freeze your laptop, so definitely consider using a beefier machine. In addition I found that installing it via Anaconda slowed me down because it inserted a lot more configuration steps so I ultimately used the pip installation process.
2. [Download the Models Repo](https://github.com/tensorflow/models). The location doesn't matter as long as you can easily cd into it.
3. Generating the research protofiles. CD into the research subfolder of the models repo and run the following command:
```
protoc object_detection\protos\anchor_generator.proto object_detection\protos\argmax_matcher.proto object_detection\protos\bipartite_matcher.proto object_detection\protos\box_coder.proto object_detection\protos\box_predictor.proto object_detection\protos\eval.proto object_detection\protos\faster_rcnn.proto object_detection\protos\faster_rcnn_box_coder.proto object_detection\protos\grid_anchor_generator.proto object_detection\protos\hyperparams.proto object_detection\protos\image_resizer.proto object_detection\protos\input_reader.proto object_detection\protos\keypoint_box_coder.proto object_detection\protos\losses.proto object_detection\protos\matcher.proto object_detection\protos\mean_stddev_box_coder.proto object_detection\protos\model.proto object_detection\protos\optimizer.proto object_detection\protos\pipeline.proto object_detection\protos\post_processing.proto object_detection\protos\preprocessor.proto object_detection\protos\region_similarity_calculator.proto object_detection\protos\square_box_coder.proto object_detection\protos\ssd.proto object_detection\protos\ssd_anchor_generator.proto object_detection\protos\string_int_label_map.proto object_detection\protos\train.proto --python_out=.
```
Theoretically you should not need to specify every proto name, but I found that this did not work on Windows machines.
4. Run the model builder test. From the research subfolder, run `python object_detection/builders/model_builder_test.py`.
5. Setup the space you'll train in. My folder looked like this:
 data (talked more in Preparing the Data)
 evaluation (will have the output of the evaluation job)
 records (will have my TensorFlow records)
 ssd_mobilenet_v1_coco_11_06_2017 (a copy of the extracted (mobilenet model)[https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) I'll retrain)
 ssd_mobilenet_v1_pets.config (copied from the (configs folder)[https://github.com/tensorflow/models/tree/master/research/object_detection/samples/configs])

## Preparing the Data
Since I wanted to be able to train multiple classes, I decided to organize the data in this folder structure:
 data
  |--->class
        |--->training
             | xml data files
             |--->images
        |--->verification
             | xml data files
             |--->images

This allowed me to keep all of my images of various types clearly separated. If you decide to use a different organization you will most likely need to change create_pascal_tf_record_custom_class.py to reflect your changes.

1. Label Images. I also used (LabelImg)[https://github.com/tzutalin/labelImg] to manually label my images. A couple of observations:
* From what I can tell, the xml files use absolute paths to the images. It seems like they should allow for relative paths as well, but I haven't tested this yet.
* One problem I did enounter were saved XML files that didn't have a height or width. This happened so often that I eventually created a one time script to print the names of all output xml files that had this problem and deleted them. Most likely these can be fixed as well, but it's a problem that can crop up.
2. Create TensorFlow Record File. I decided to use models-master/research/object_detection/dataset_tools/create_pascal_tf_record.py to generate the record file, but found that it was only set to train the aeroplane class and assumed all of your data was in the original dataset. Since I'm using my own data and classes I created create_pascal_tf_record_custom_class.py to easily use new data and classes. Run it like so from your project directory:
```
    python create_pascal_tf_record_custom_class.py \
        --data_dir=data \
        --custom_class=pose \
        --training_type=training \
        --output_path=records/pose_training.record \
        --label_map_path=pascal_label_map.pbtxt
```
You'll run it twice for each class: once for your training set, once for your verification set. Make sure to use different paths for each record to avoid overwriting your record file.

## Final Setup
1. Open ssd_mobilenet_v1_pets.config and go to each place that says "PATH_TO_BE_CONFIGURED". You'll want to put an absolute path to the particular file.
* On Windows I had to use double slashes (//) for the paths to be correctly interpreted.
* The `input_path` field supports multiple record files. Have all of the paths in one string, separated by semicolons. For example: 
```
input_path:"C:\\project_folder\\records\\class1_training.record;C:\\project_folder\\records\\class2_training.record"
```
2. Still in ssd_mobilenet_v1_pets.config, find `num_classes` and set it to the number of classes you should use.

## Training
You'll want to open 3 terminals, since there are three jobs to run.
1. The Training Job. Get to the research subdirectory of the models repo and run
```
python object_detection/train.py --logtostderr --pipeline_config_path=C:\project_folder\ssd_modilenet_v1_pets.config --train_dir=C:\project_folder\ssd_mobilenet_v1_coco_11_06_2017
```
To capture all of the output into a file (which is useful while debugging this), Windows users can use this variation of the command:
```
python object_detection/train.py --logtostderr --pipeline_config_path=C:\project_folder\ssd_modilenet_v1_pets.config --train_dir=C:\project_folder\ssd_mobilenet_v1_coco_11_06_2017 > training_log.txt 2>&1 
```
Note this will put the training log into the research folder rather than your project folder. Most likely you can use an absolute path to get around that problem.
2. The Evaluation Job. Get to the research subdirectory of the models repo and run
```
python object_detection/eval.py --logtostderr --pipeline_config_path=C:\project_folder\ssd_modilenet_v1_pets.config --train_dir=C:\project_folder\ssd_mobilenet_v1_coco_11_06_2017 --eval_dir=C:\project_folder\evaluation
```
3. TensorBoard, which allows you to monitor your progress. Run this from anywhere:
```
tensorboard --logdir=C:\project_folder
```

In a few minutes you should be able to go to the URL that's specified in the tensorboard window and see the model retraining with your class and data!

