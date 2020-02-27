from gpiozero import MotionSensor
import picamera
import time
import subprocess

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

BASE_PATH = '/home/pi/scripts/Motion/images/'
GMAIL_U = 'john.christian.private@gmail.com'
GMAIL_P = 'xxxxxxxxxxxxxxxxxxxxxxx'

import smtplib
import os.path as op
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders


def send_mail(send_from, send_to, subject, message, files=[],
              server="smtp.gmail.com", port=587, username=GMAIL_U, password=GMAIL_P,
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (str): to name
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(op.basename(path)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
    

#where is the pir sensor
pir = MotionSensor(4)

def detectMotion():
    pir.wait_for_motion()

def handleMotion():
    print("Motion")

def detectStill():
    pir.wait_for_no_motion()

def handleStill():
    print("Still")

def talkToCamera(): 
    secSinceEpock = str(time.time())
    #secSinceEpock = 'test'
    print ( "Taking Picture")
    img = BASE_PATH+secSinceEpock+".jpg"
    print (img)
    
    with picamera.PiCamera() as camera:
        camera.resolution = (1280,720)
        camera.capture(img)

    return img

def showImage(img):
    #Display the image
    image = subprocess.Popen(["feh", "--hide-pointer", "-x", "-q", "-B", "black", "-g", "1280x720",img])

    send_mail(GMAIL_U,[GMAIL_U], "Someone's at the door", "Who dat?", [img]);

    time.sleep(5);
    image.kill()
    

try:
    while 1:

        #wait for something to move.
        detectMotion()
        handleMotion()

        #take a piccy
        img = talkToCamera();

        #showToScreen
        showImage(img)
        

        #wait for it to stop
        detectStill()
        handleStill()

finally:
    print("Exit program")
