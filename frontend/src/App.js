import React, { useState } from "react";
import "./App.css";
import { getDocument, GlobalWorkerOptions } from "pdfjs-dist/build/pdf";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";

GlobalWorkerOptions.workerSrc = pdfjsWorker;

const AnnotatedData = ({ annotatedData, selected, setSelected }) => {
  const handleSelect = (id) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((i) => i !== id));
      return;
    }
    setSelected([...selected, id]);
  };

  const bgColors = ["bg-emerald-200", "bg-amber-200", "bg-rose-200"];

  return (
    <div className="mb-4 leading-10">
      {annotatedData.map((data, index) => {
        const bgColor = bgColors[index % bgColors.length];
        return (
          <p
            key={index}
            className={`rounded-md hover:bg-cyan-200 break-words inline p-2 cursor-pointer select-none ${
              selected.includes(data.id) ? "bg-zinc-300" : bgColor
            }`}
            onClick={() => handleSelect(data.id)}
            title={data.factors.join(", ")}
          >
            <span className="bg-white rounded-md p-1">
              {data.factors.join(", ")}
            </span>{" "}
            {data.text_extract}
            {". "}
          </p>
        );
      })}
    </div>
  );
};

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [annotatedData, setAnnotatedData] = useState([]);
  const [documentUpload, setDocumentUpload] = useState(null);
  const [uniqueFactors, setUniqueFactors] = useState([]);
  const [sentences, setSentences] = useState([]);

  const [selectedSentenceIds, setSelectedSentenceIds] = useState([]);

  const fetchAnnotationsData = async (sentences) => {
    setIsLoading(true);
    const res = await fetch("http://localhost:5000/api/annotate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text_extracts: sentences,
        text_extract_ids: selectedSentenceIds,
      }),
    });
    const data = await res.json(); //annotatedDataMock; //

    setIsLoading(false);
    return data;
  };

  const parseAnnotations = (data) => {
    const newAnnotatedData = data.annotations || [];
    const newUniqueFactors = data.unique_factors || [];

    setAnnotatedData(newAnnotatedData);
    setUniqueFactors(newUniqueFactors);
  };

  const updateAnnotations = async () => {
    const data = await fetchAnnotationsData(sentences);

    const newAnnotatedData = data.annotations || [];

    if (newAnnotatedData.length === 0) {
      return;
    }

    console.log("New Annotated Data:", newAnnotatedData);

    const updatedAnnotatedData = annotatedData.map((obj) => {
      const newData = newAnnotatedData.find((d) => d.id === obj.id);
      if (newData) {
        return newData;
      }
      return obj;
    });
    const newUniqueFactors = data.unique_factors || [];

    setAnnotatedData(updatedAnnotatedData);
    setUniqueFactors([...uniqueFactors, ...newUniqueFactors]);
  };

  const handleDocumentChange = (event) => {
    setDocumentUpload(event.target.files[0]);
  };

  const handleUpload = async () => {
    setSelectedSentenceIds([]);
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
        setSentences(sentences);
        const data = await fetchAnnotationsData(sentences);
        parseAnnotations(data);
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
            <h1 className="text-center text-1xl font-bold">Controls</h1>

            <input type="file" onChange={handleDocumentChange} />
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              onClick={handleUpload}
              disabled={isLoading}
            >
              Upload
            </button>
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              onClick={updateAnnotations}
              disabled={isLoading}
            >
              Redo
            </button>
          </div>
          <div className="flex flex-col gap-4 mt-5">
            <h1 className="text-center text-1xl font-bold">Taxonomy</h1>
            <div className="flex flex-col max-h-96 gap-4 overflow-y-scroll">
              {uniqueFactors
                ? uniqueFactors.map((factor, index) => (
                    <div
                      key={index}
                      className="hover:bg-blue-100 rounded-md p-2"
                    >
                      {factor.code_id}: {factor.code}
                    </div>
                  ))
                : "No factors"}
            </div>
          </div>
          <div className="flex flex-col gap-4 mt-5">
            <h1 className="text-center text-1xl font-bold">Research</h1>
          </div>
        </section>
        <section className="items-center flex-grow border border-gray-500 shadow-md p-5">
          {isLoading ? (
            <div className="text-center">Loading...</div>
          ) : (
            <AnnotatedData
              annotatedData={annotatedData}
              selected={selectedSentenceIds}
              setSelected={setSelectedSentenceIds}
            />
          )}
        </section>
      </div>
    </main>
  );
}

export default App;
