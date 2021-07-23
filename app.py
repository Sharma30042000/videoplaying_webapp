import re
from flask import Flask,render_template,jsonify
from flask.templating import render_template, render_template_string
from werkzeug.datastructures import RequestCacheControl
from flask import request
from config import S3_KEY, S3_SECRET, S3_BUCKET
import boto3
from datetime import datetime
app=Flask("sagar")
from flask_mysqldb import MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'kidsdb'
app.config['FLASK_ENV'] = 'development'
mysql = MySQL(app)
@app.route("/", methods=["GET","POST"])
def home():
     if request.method == "POST":
          search_txt=request.form.get("search_txt")
          cur=mysql.connection.cursor()
          cur.execute(f"SELECT * FROM persons WHERE Title LIKE '%{search_txt}%'")
          rows = cur.fetchall()
          cur.close()
          payload = []
          content = {}
          for result in rows:
               content = {'user_id': result[0], 'UserName': result[1], 'Title': result[2],'Caption': result[3],'Video_URL': result[4],'Image_URL': result[5],'vid_date': result[6],'vid_type': result[7]}
               payload.append(content)
               content = {}
          rows=payload
          return render_template("home.html",rows=rows,dflt=search_txt)
  
     cur=mysql.connection.cursor()
     cur.execute("SELECT * FROM persons")
     rows = cur.fetchall()
     cur.close()
     payload = []
     content = {}
     for result in rows:
               content = {'user_id': result[0], 'UserName': result[1], 'Title': result[2],'Caption': result[3],'Video_URL': result[4],'Image_URL': result[5],'vid_date': result[6],'vid_type': result[7]}
               payload.append(content)
               content = {}
     rows=payload
     print(rows)
     return render_template("home.html",rows=rows,dflt="")

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET

)
@app.route("/form")
def form():
     return render_template("form.html")

@app.route("/videos",methods=["GET","POST"])
def videos():
     try:
          username=request.form.get("username")
          title=request.form.get("title")
          discription=request.form.get("caption")
          video=request.files["video"]
          vid_type=video.content_type
          image=request.files["image"]
          file_name=video.filename
          image_file_name=image.filename
          s3.upload_fileobj(
                 video,
                 S3_BUCKET,
                 video.filename,
                 ExtraArgs={
                           "ACL": "public-read",
                           "ContentType": video.content_type
                           },        
                ) 
          s3.upload_fileobj(
                image,
                S3_BUCKET,
                 image.filename,
                 ExtraArgs={
                           "ACL": "public-read",
                           "ContentType": video.content_type
                      },        
                 )
          now = datetime.now()
          formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
          
          aws_region= boto3.client('s3').get_bucket_location(Bucket=S3_BUCKET)['LocationConstraint']
          video_url=f"https://{S3_BUCKET}.s3.{aws_region}.amazonaws.com/{file_name}"
          image_url=f"https://{S3_BUCKET}.s3.{aws_region}.amazonaws.com/{image_file_name}"
          cur = mysql.connection.cursor()
          print("errroeoeoeo")
          print((username,title,discription,video_url,image_url,formatted_date))
          cur.execute("INSERT INTO persons (UserName,Title,Caption,Video_URL,Image_URL,vid_date,vid_type) VALUES (%s,%s,%s,%s,%s,%s,%s)", (username,title,discription,video_url,image_url,formatted_date,vid_type))
          print("okok")
          mysql.connection.commit()
          cur.close()
     except:
          return render_template("form.html")
     cur=mysql.connection.cursor()
     cur.execute("SELECT * FROM persons")
     rows = cur.fetchall()
     cur.close()
     payload = []
     content = {}
     for result in rows:
               content = {'user_id': result[0], 'UserName': result[1], 'Title': result[2],'Caption': result[3],'Video_URL': result[4],'Image_URL': result[5],'vid_date': result[6],'vid_type': result[7]}
               payload.append(content)
               content = {}
     rows=payload
     print(rows)
     return render_template("home.html",rows=rows,dflt="")
    
    


@app.route('/search',methods=["GET","POST"])
def search():
     if request.method == "POST":
          search_txt=request.form.get("search_txt")
          cur=mysql.connection.cursor()
          cur.execute(f"SELECT * FROM persons WHERE Title LIKE '%{search_txt}%'")
          rows=cur.fetchall()
          cur.close()
          return render_template("home.html",rows=rows,dflt=search_txt)
  
     cur=mysql.connection.cursor()
     cur.execute("SELECT * FROM persons")
     rows = cur.fetchall()
     cur.close()
     return render_template("home.html",rows=rows)

     
    
if __name__ == "__main__":
    app.run(debug=True)