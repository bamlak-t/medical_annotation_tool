import React, { useState } from "react";
import "./App.css";

import { annotated_data_mock } from "./mock/mock_data";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [annotated_data, setAnnotated_data] = useState([]);
  const [documentUpload, setDocumentUpload] = useState(null);

  const fetchAnnotations = async () => {
    setIsLoading(true);
    // const res = await fetch("http://localhost:5000/api/endpoint");
    // const data = await res.json();
    setAnnotated_data(annotated_data_mock);
    setIsLoading(false);
  };

  const handleDocumentChange = (event) => {
    setDocumentUpload(event.target.files[0]);
  };

  const handleUpload = () => {
    if (documentUpload) {
      console.log("Uploading file:", documentUpload.name);
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
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={fetchAnnotations}
        disabled={isLoading}
      >
        {isLoading ? "Loading..." : "Fetch Data"}
      </button>
      <div className="flex flex-row w-full gap-10">
        <section className="justify-center items-center border border-gray-500 shadow-md p-5 min-w-80">
          <div className="flex flex-col gap-4">
            <h1 className="text-center text-1xl font-bold">Upload</h1>

            <input type="file" onChange={handleDocumentChange} />
            <button onClick={handleUpload}>Upload</button>
          </div>
          <div className="flex flex-col gap-4">
            <h1 className="text-center text-1xl font-bold">Research</h1>
          </div>
        </section>
        <section className="items-center flex-grow border border-gray-500 shadow-md p-5">
          <div className="mb-4">
            {annotated_data.map((data, index) => (
              <p
                key={index}
                className="hover:text-blue-500 break-words inline"
                title={data.factors.join(", ")}
              >
                {data.text_extract}{" "}
              </p>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

export default App;
