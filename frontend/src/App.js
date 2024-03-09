import React, { useState } from "react";
import "./App.css";
import { getDocument, GlobalWorkerOptions } from "pdfjs-dist/build/pdf";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";

GlobalWorkerOptions.workerSrc = pdfjsWorker;

const AnnotatedData = ({ annotatedData }) => {
  console.log("Annotated Data:", annotatedData);
  return (
    <div className="mb-4">
      {annotatedData.map((data, index) => (
        <p
          key={index}
          className="hover:text-blue-500 break-words inline"
          title={data.factors.join(", ")}
        >
          {data.text_extract}
          {". "}
        </p>
      ))}
    </div>
  );
};

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [annotatedData, setAnnotatedData] = useState([]);
  const [documentUpload, setDocumentUpload] = useState(null);

  const fetchAnnotations = async (sentences) => {
    setIsLoading(true);
    // const res = await fetch("http://localhost:5000/api/endpoint");
    // const data = await res.json();
    const annotatedData = sentences.map((sentence) => {
      return {
        text_extract: sentence,
        factors: ["Factor 1", "Factor 2"],
      };
    });

    setAnnotatedData(annotatedData);
    setIsLoading(false);
  };

  const handleDocumentChange = (event) => {
    setDocumentUpload(event.target.files[0]);
  };

  const handleUpload = async () => {
    console.log("Uploading file...");
    if (documentUpload) {
      console.log("Uploading file:", documentUpload.name);

      const fileReader = new FileReader();
      fileReader.onload = async (e) => {
        const content = e.target.result;
        const pdf = await getDocument(content).promise;
        const page = await pdf.getPage(1); // get first page
        const textContent = await page.getTextContent();
        const segments = textContent.items.map((item) => item.str);
        const sentences = segments
          .join("")
          .split(/[.!?]/)
          .filter((sentence) => sentence.trim() !== "")
          .map((sentence) => sentence.trim());
        console.log("Sentences:", sentences);
        await fetchAnnotations(sentences);
      };
      fileReader.readAsArrayBuffer(documentUpload); // read as ArrayBuffer for pdf.js
    } else {
      console.log("No file selected");
    }
  };

  return (
    <main className="flex flex-col min-h-screen items-center">
      <div className="w-full h-20 mb-8 border border-gray-500 shadow-md">
        <h1 className="text-4xl font-bold flex pt-4 pl-5">
          Medical Annotation Tool
        </h1>
      </div>

      <div className="flex flex-row w-full gap-10">
        <section className="justify-center items-center border border-gray-500 shadow-md p-5 min-w-80">
          <div className="flex flex-col gap-4">
            <h1 className="text-center text-1xl font-bold">Upload</h1>

            <input type="file" onChange={handleDocumentChange} />
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              onClick={handleUpload}
              disabled={isLoading}
            >
              Upload
            </button>
          </div>
          <div className="flex flex-col gap-4 mt-5">
            <h1 className="text-center text-1xl font-bold">Research</h1>
          </div>
        </section>
        <section className="items-center flex-grow border border-gray-500 shadow-md p-5">
          {isLoading ? (
            <div className="text-center">Loading...</div>
          ) : (
            <AnnotatedData annotatedData={annotatedData} />
          )}
        </section>
      </div>
    </main>
  );
}

export default App;
