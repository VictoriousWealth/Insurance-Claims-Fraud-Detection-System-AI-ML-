import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/data")  // Fetch from FastAPI
      .then(response => setData(response.data))
      .catch(error => console.error("Error fetching data:", error));
  }, []);

  return (
    <div>
      <h1>React + FastAPI Integration</h1>
      {data ? (
        <div>
          <p>X values: {data.x.join(", ")}</p>
          <p>Y values: {data.y.join(", ")}</p>
        </div>
      ) : (
        <p>Loading data...</p>
      )}
      <iframe
        src="http://127.0.0.1:8000/dash"
        width="100%"
        height="500px"
        title="Dash App"
      />
    </div>
  );
}

export default App;
