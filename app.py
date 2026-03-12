from flask import Flask, render_template, request, send_file
import statistics
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from reportlab.pdfgen import canvas

app = Flask(__name__)

last_data = []
last_graph = "bar"

@app.route("/", methods=["GET","POST"])
def index():

    global last_data

    result=None
    data=[]

    if request.method=="POST":

        numbers=request.form["numbers"]
        data=[float(x) for x in numbers.split(",")]

        last_data=data

        result={
        "sum":sum(data),
        "mean":round(statistics.mean(data),2),
        "median":statistics.median(data),
        "min":min(data),
        "max":max(data),
        "range":max(data)-min(data),
        "q1":np.percentile(data,25),
        "q2":np.percentile(data,50),
        "q3":np.percentile(data,75)
        }

        result["iqr"]=result["q3"]-result["q1"]

        lower=result["q1"]-1.5*result["iqr"]
        upper=result["q3"]+1.5*result["iqr"]

        outliers=[x for x in data if x<lower or x>upper]

        result["outliers"]=outliers if outliers else "None"

    return render_template("index.html",result=result,data=data)



@app.route("/download_pdf",methods=["POST"])
def download_pdf():

    global last_data,last_graph

    graph_type=request.form["graphType"]
    last_graph=graph_type

    data=last_data

    freq={}
    for i in data:
        freq[i]=freq.get(i,0)+1

    labels=list(freq.keys())
    values=list(freq.values())

    img=io.BytesIO()

    plt.figure()

    if graph_type=="bar":
        plt.bar(labels,values)

    elif graph_type=="line":
        plt.plot(labels,values)

    elif graph_type=="pie":
        plt.pie(values,labels=labels,autopct="%1.1f%%")

    plt.title("Data Graph")

    plt.savefig(img,format="png")
    plt.close()

    img.seek(0)

    buffer=io.BytesIO()

    c=canvas.Canvas(buffer)

    c.drawString(200,800,"Statistical Analysis Report")
    c.drawString(50,760,f"Data: {data}")

    with open("graph.png","wb") as f:
        f.write(img.getbuffer())

    c.drawImage("graph.png",100,400,width=400,height=300)

    c.save()

    buffer.seek(0)

    return send_file(buffer,as_attachment=True,download_name="report.pdf",mimetype="application/pdf")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
