# -*- coding: utf-8 -*-
"""Git Fuzzy Logic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12UwWXuBF0fGPMW8jgwWypRaiz1lAeVGO

# Extracting Angular Features
"""

import cv2
import numpy as np
import math
from PIL import Image
from sklearn import svm
import keras
from sklearn.svm import SVC
size=8

def make_12_parts(lrpart,img):
  partition = np.empty(shape=(size,40,60))
  crop_img=np.empty(shape=(96,10,20))
  x=0
  for k in range(1,size):
    a = lrpart[k-1] 
    b = lrpart[k]
    part = img[:,int(a):int(b)]
    part = cv2.resize(img,(60,40))
    #insert function to partition into 12ths
    partition[k]=part #contains the 8 resized partitions
  for m in range(0,size):
    part_k = partition[m]
    for i in range(0,60,20):
      for j in range(0,40,10):
        crop_img[x] = part_k[j:j+10,i:i+20]
        x+=1
       
  return crop_img

def make_8_parts(img):
  #This is for implementing horizontal density and making partitions
  #First we identify the number of dark pixels
  n=120
  m=60
  dark = 0 #total number of dark pixels
  col_pix=0 #no of pixels that should be within a partition
  x=1
  size=8 #no of partitions I want
  tot_pix=0
  lpart = np.zeros(shape=size+1)
  rlpart = np.zeros(shape=size+1)
  for i in range(0,n):
      for j in range(0,m):
        if(img[j,i]<200):
          dark+=1
  no_of_pixels= math.floor(dark/size)
  #counting pixels from left to right
  for j in range(0,n): 
    for i in range(0,m):
      if(img[i,j]<200):
        col_pix+=1
    if(col_pix<no_of_pixels):
      continue
    else:
      lpart[x]=j
      x+=1
      tot_pix=tot_pix+col_pix
      col_pix=0
  remaining = dark - tot_pix
  jnew = j
  if(remaining!=0):  
    if((remaining)<no_of_pixels):
      if(x<size):
        for j in range (jnew, n):
          for i in range(0,m):
            if(img[i,j]<200):
              col_pix+=1
          if(col_pix==remaining):
            lpart[x]=j
      else:
        lpart[x-1]=n
  x=1
  #counting pixels from right to left
  for j in range(n-1,-1,-1): 
    for i in range(0,m):
      if(img[i,j]<200):
        col_pix+=1
    if(col_pix<no_of_pixels):
      continue
    else:
      rlpart[x]=j
      x+=1
      tot_pix=tot_pix+col_pix
      col_pix=0
  remaining = dark - tot_pix
  jnew = j
  if(remaining==0):
    add_parts = lpart+rlpart
    partition_result = np.divide(add_parts,2)
    for f in range(0,size):
      partition_result[f] = math.floor(partition_result[f])
    return partition_result
  if((remaining)<no_of_pixels):
    for j in range (jnew, n):
      for i in range(0,m):
        if(img[i,j]<200):
          col_pix+=1
      if(col_pix==remaining):
        rlpart[x]=j
  add_parts = lpart+rlpart
  partition_result = np.divide(add_parts,2)
  for f in range(0,size):
    partition_result[f] = math.floor(partition_result[f])
  return partition_result

def angle_extraction(crop_img):
  n=10
  m=20
  angle_features = np.empty(shape=96)
  for c in range(0,96):
    img = crop_img[c]
    sum=0
    dark=0
    for i in range(0,n):
      for j in range(0,m): 
        if(img[i,j]!=255):
          dark+=1
          x=j+1
          y=n+1-i
          dist = np.sqrt(np.power(x,2)+np.power(y,2))
          ang = np.arctan(y/x)
          sum = sum+ang
        else:
          continue
    if(sum==0):
      angle_features[c]=0
      continue
    angle_features[c] = sum/dark
  return angle_features

"""# Retrieving Information Set (GPDS Dataset)"""

u = 5 #to denote the user
size = 8
label_train = np.zeros(shape=36)
label_test = np.zeros(shape=12) 
test_iter=0
train_iter=0
count = 0 
angle_features = np.zeros(shape=(24,96))

for p in range(1,10):
    im = cv2.imread("c-00"+str(u)+"-0"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(im, (120,60)) 
    label_train[train_iter]=1 
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img)
    angle_features[p-1] = angle_extraction(crop_img) 
    count+=1
    train_iter+=1
for p in range(10,19):
    print("Scanning Image:",p)
    im = cv2.imread("c-00"+str(u)+"-"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    label_train[train_iter]=1
    img = cv2.resize(im, (120,60)) 
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img) 
    angle_features[p-1] = angle_extraction(crop_img)
    count+=1
    train_iter+=1
for p in range(19,25): 
    print("Scanning Image:",p)
    im = cv2.imread("c-00"+str(u)+"-"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    label_test[test_iter]=1
    img = cv2.resize(im, (120,60)) 
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img)
    angle_features[p-1] = angle_extraction(crop_img)
    count+=1
    test_iter+=1

angle_features_forged = np.zeros(shape=(24,96))
for p in range(1,10):
    im = cv2.imread("c-00"+str(u)+"-0"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    print("Scanning Image:",p)
    img = cv2.resize(im, (120,60))
    label_train[train_iter]= 0 
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img)
    angle_features_forged[p-1] = angle_extraction(crop_img)
    count+=1
    train_iter+=1
for p in range(10,19):
    print("Scanning Image:",p)
    im = cv2.imread("c-00"+str(u)+"-"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    label_train[train_iter]= 0
    img = cv2.resize(im, (120,60)) 
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img)
    angle_features_forged[p-1] = angle_extraction(crop_img)
    count+=1
    train_iter+=1
for p in range(19,25):
    print("Scanning Image:",p)
    im = cv2.imread("c-00"+str(u)+"-"+str(p)+".jpg", cv2.IMREAD_GRAYSCALE)
    label_test[test_iter]=0
    img = cv2.resize(im, (120,60))
    lrpart = make_8_parts(img)
    crop_img = make_12_parts(lrpart, img)
    angle_features_forged[p-1] = angle_extraction(crop_img)
    count+=1
    test_iter+=1

train_features = np.zeros(shape=(36,96))
test_features = np.zeros(shape=(12,96))
train_features[0:18] = angle_features[0:18]
genuine_features = angle_features[0:18]
train_features[18:36] = angle_features_forged[0:18]
test_features[0:6] = angle_features[18:24]
test_features[6:12] = angle_features_forged[18:24]

#TO CALCULATE STATISTICS - MEAN AND VARIANCE FOR EACH OF THE 96 FEATURES
angular_features_mean = np.zeros(shape=(96))
angular_features_variance = np.zeros(shape=(96))
diff1 = np.zeros(shape=(18,96))
for x in range(0,96): #iterating over each fuzzy set because there are 96 fuzzy sets for 96 features
  angular_features_mean[x] = np.mean(angle_features[0:18,x])
  angular_features_variance[x] = np.var(angle_features[0:18,x])

#TO CALCULATE MEMBERSHIP FUNCTION
membership_train = np.zeros(shape=(36,96))
for j in range(0,36): 
  for k in range(0,96):
    numerator = np.power((train_features[j,k]-angular_features_mean[k]),2)
    denominator = 2*np.power(angular_features_variance[k],2)
    #calculating Gaussian function
    if(numerator==0):
      membership_train[j,k] = 0
    else:
      frac = -1*numerator/denominator
      membership_train[j,k] = np.exp(-(np.power((train_features[j,k]-angular_features_mean[k]),2))/(2*np.power(angular_features_variance[k],2)))

genuine_train = np.zeros(shape=(18,96))
for j in range(0,18):
  for k in range(0,96):
    numerator = np.power((genuine_features[j,k]-angular_features_mean[k]),2)
    denominator = 2*np.power(angular_features_variance[k],2)
    if(numerator==0):
      frac=0
    else:
      frac = -1*numerator/denominator
    genuine_train[j,k] = np.exp(frac)

membership_test = np.zeros(shape=(12,96))
for j in range(0,12):
  for k in range(0,96):
    numerator = np.power((test_features[j,k]-angular_features_mean[k]),2)
    denominator = 2*np.power(angular_features_variance[k],2)
    if(numerator==0):
      frac=0
    else:
      frac = -1*numerator/denominator
    membership_test[j,k] = np.exp(frac)

#applying entropy function to get the info sets for both genuine and forged signatures
info_set_train = np.zeros(shape=np.shape(membership_train)) #36, 96
info_set_test = np.zeros(shape=np.shape(membership_test))
genuine_infoset = np.zeros(shape=np.shape(genuine_train))
for j in range(0,36): #since we only consider training images, ando no_forgeries = no_genuine while training
  for k in range(0,96):
    info_set_train[j,k] = train_features[j,k]*membership_train[j,k]
for j in range(0,12): 
  for k in range(0,96): 
    info_set_test[j,k] = test_features[j,k]*membership_test[j,k]
for j in range(0,18): 
  for k in range(0,96): 
    genuine_infoset[j,k] = genuine_features[j,k]*genuine_train[j,k]

#Here we apply a transform to the Information set by applying sigmoid function.
transformed_is_train = 1/(1+np.exp(-(info_set_train)))
transformed_is_test = 1/(1+np.exp(-(info_set_test)))

"""# SVM With Information Set"""

#we train a different SVM for each single user.
model_svm = SVC(kernel="rbf", gamma = 1, degree=1)
model_svm.fit(transformed_is_train,label_train)
#score = model_svm.score(transformed_is_test,label_test)
score = model_svm.score(transformed_is_train, label_train)
print(score)
predicted = model_svm.predict(transformed_is_train)

"""# Hanman Classifier

**Brief Explanation**

Our training vectors have a size of 18x96 because we have 18 signatures (genuine) and 96 features per signature - we are using information sets here. We choose a test vector and subtract its values from each of the 18 training samples. This gives rise to 18 error vectors of size 96, for each test signature.
At this point we want to apply t-norm and s-norm so as to extend the boundary of the margin which distinguishes between two classes. This extension of the boundary will allow us some extra space on the sides so genuine signatures are not falsely classified as forged. We use t-norm to identify the minimum of this range and s-norm to identify the maximum of the range.
We use Frank t-norm and s-norm for this purpose. We consider all combinations of two error vectors from the 18 we calculated. Out of these combinations, we want to identify the minimum of all these error vectors - so this defines the minimum point of our boundary. We use s-norm for the maximum.
Hence we have a range for each signature, and we choose a test signature as reference in order to see how its parameters compare with the established minimum and maximum.
"""

#Calculating error vector
test_reference_number = 1 #It should lie in between 0-5 as 6-11 are forged
test_reference = info_set_test[test_reference_number]
#calculating error vectors
error_vector = np.zeros(shape=(18,96))
for j in range(0,18):
  for k in range(0,96):
    difference = test_reference[k]-genuine_infoset[j,k]
    error_vector[j,k] = np.absolute(difference)

n=18
p=2
t_norm = np.zeros(shape=(153,96))
s_norm = np.zeros(shape=(153,96))
count=0
for j in range(0,n-1):
  ej = error_vector[j]
  for k in range(j+1,n):
    ek = error_vector[k]
    a_t = np.power(p,ej)-1
    b_t = np.power(p,ek)-1
    exp_t = (np.multiply(a_t,b_t)/(p-1))+1
    for i in range(0,96):
      t_norm[count,i] = math.log(exp_t[i],p)
    a_s = np.power(p,1-ej) - 1
    b_s = np.power(p,1-ek) - 1
    exp_s = (np.multiply(a_s,b_s)/(p-1))+1
    for i in range(0,96):
      s_norm[count,i] = 1-math.log(exp_s[i],p)
    count+=1

#now we want to calculate the minimum of all 171 samples per feature and then the maximum of all 171 samples per feature
min_tnorm = np.zeros(shape=(96))
max_snorm = np.zeros(shape=(96))
for i in range(0,96):
  min_tnorm[i] = min(t_norm[:,i])
  max_snorm[i] = max(s_norm[:,i])
print(min_tnorm)
print(max_snorm)

test_sample_number1 = 6
test_sample1 = info_set_test[test_sample_number1]
#calculating error vectors
test_error_vector1 = np.absolute(test_reference - test_sample1)
test_sample_number2 = 10 #It should lie in between 0-5 as 6-11 are forged, and not be the reference no either
test_sample2 = info_set_test[test_sample_number2]
#calculating error vectors
test_error_vector2 = np.absolute(test_reference - test_sample2)

#calculating t norm and s norm
t_norm_test = np.zeros(shape=96)
s_norm_test = np.zeros(shape=96)
a = np.power(p,test_error_vector1)-1
b = np.power(p,test_error_vector1)-1
product1 = 1+(np.multiply(a,b)/(p-1))
for i in range(0,96):
  t_norm_test[i] = math.log(product1[i],p)
  
c = np.power(p,1-test_error_vector1)-1
d = np.power(p,1-test_error_vector1)-1
product2 = 1+(np.multiply(a,b)/(p-1))
for i in range(0,96):
  s_norm_test[i] = 1-(math.log(product2[i],p))

res1 = s_norm_test - max_snorm
res2 = t_norm_test - min_tnorm