import React, {useEffect, useState} from "react";
import axios from "axios";
import '../styles/home.css'

export default function Home() {
    /* 
    Component for home page
    */
    const [message, setMessage] = useState("");

    // get message from backend
    useEffect(() => {
        axios.get("http://localhost:5000/api/message")
        .then(res => setMessage(res.data.message))
        .catch(err => console.error(err));
    }, []);

    return (
        <>
            <div className="home">
                <div className="home-card">
                    <h1 className="home-title">Message from Flask:</h1>
                    <p className="home-message">{message}</p>
                    <p className="home-subtext">Home page demo</p>
                </div>
            </div>
        </>
    );
}