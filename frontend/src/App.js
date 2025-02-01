import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [employees, setEmployees] = useState(null);
  const [insurance, setInsurance] = useState(null);
  const [vendors, setVendors] = useState(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/employees")
      .then(response => setEmployees(response.data))
      .catch(error => console.error("Error fetching employees:", error));

    axios.get("http://127.0.0.1:8000/api/insurance")
      .then(response => setInsurance(response.data))
      .catch(error => console.error("Error fetching insurance:", error));

    axios.get("http://127.0.0.1:8000/api/vendors")
      .then(response => setVendors(response.data))
      .catch(error => console.error("Error fetching vendors:", error));
  }, []);

  return (
    <div style={{width: 95 +'%'}}>
      <h1>Insurance Claims Fraud Detection System</h1>
      <iframe
        src="http://127.0.0.1:8000/dash"
        width="100%"
        height="500px"
        title="Dash App"
        style={{marginLeft: 2.5+'%'}}
      />
    </div>
  );
}

export default App;
