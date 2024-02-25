import Image from "next/image";

export default function Home() {
  return (
    <main className="flex flex-col min-h-screen items-center">
      <div className="w-full h-20 mb-8 border border-gray-500 shadow-md">
        <h1 className="text-4xl font-bold flex pt-4 pl-5">
          Medical Annotation Tool
        </h1>
      </div>
      <div className="flex flex-row w-full gap-10">
        <section className="justify-center items-center border border-gray-500 shadow-md p-5 min-w-80">
          <h1 className="text-center text-1xl font-bold">Research</h1>
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
