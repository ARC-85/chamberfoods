#importing required libraries
import firebase_admin
from firebase_admin import credentials, storage, db
import os

#read Firebase credentials from serviceAccountKey.json file
cred=credentials.Certificate('./serviceAccountKey.json')

#initialise Firebase app
firebase_admin.initialize_app(cred, {
    'storageBucket': '', #define storage 
    'databaseURL': 'https://' #define database url
})

bucket = storage.bucket() #define variable for storage bucket

#defining home reference within Realtime DB
ref = db.reference('/') 
home_ref = ref.child('file')

#function for storage of files in Firebase
def store_file(fileLoc):

    filename=os.path.basename(fileLoc)

    # Store File in FB Bucket
    blob = bucket.blob(filename)
    outfile=fileLoc
    blob.upload_from_filename(outfile)

#function for pushing files to Realtime DB
def push_db(fileLoc, time):

  filename=os.path.basename(fileLoc)

  # Push file reference to image in Realtime DB
  home_ref.push({
      'image': filename,
      'timestamp': time}
  )

