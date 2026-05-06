import React, { useState, useRef } from 'react';
import './CallInterface.css';

/**
 * CallInterface — Citizen call simulator for the demo.
 * Allows text input and audio recording to test the VaakSetu pipeline.
 */

const SAMPLE_QUERIES = [
  { label: "Ration Card (Kannada)", text: "Nanna ration card update aagilla, mooru tingalu aaytu application haakiddu, yenu aagide gottilla", language: "kannada" },
  { label: "Water Supply (Kannada)", text: "Namm area alli neeru barilla, eradu dina aaytu, BWSSB ge phone maadidru yaaradru phone ettilla", language: "kannada" },
  { label: "Pension Delay (Kannada)", text: "Nanna ajji ge pension baribeku ittu, mooru tingalu aaytu barilla, dayavittu sahaya maadi", language: "kannada" },
  { label: "Road Pothole (English)", text: "There is a very dangerous pothole on the main road in Jayanagar 4th Block, near the bus stop. Two accidents have already happened.", language: "english" },
  { label: "Land Dispute (Kannada)", text: "Namm hola jamin survey number 78 alli problem ide, pakkada mane avru namm jaaga tagondu idare, bhoomi record alli confusion ide", language: "kannada" },
  { label: "Emergency Distress", text: "HELP! Please turant sahaya beku, namma mane pakka tree beelide, current wire mele biddide, bahut dangerous hai!!", language: "kannada-english" },
  { label: "Garbage (Hindi)", text: "Teen din se kachra nahi uthaya gaya hai, BBMP wale koi dhyan nahi de rahe, bahut gandagi ho gayi hai", language: "hindi" },
  { label: "Seva Sindhu Status", text: "Naan income certificate ge Seva Sindhu nalli apply maadidde, ondu tingalu aaytu, application status check maadoke gottilla", language: "kannada" },
];

export default function CallInterface({ onSubmitText, onSubmitAudio, isProcessing }) {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('kannada');
  const [dialect, setDialect] = useState('standard');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  const handleSubmitText = () => {
    if (!text.trim() || isProcessing) return;
    onSubmitText?.(text.trim(), language, dialect);
  };

  const handleSampleQuery = (sample) => {
    setText(sample.text);
    setLanguage(sample.language);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());
        onSubmitAudio?.(blob, language, dialect);
        clearInterval(timerRef.current);
        setRecordingDuration(0);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingDuration(0);
      timerRef.current = setInterval(() => {
        setRecordingDuration(d => d + 1);
      }, 1000);
    } catch (err) {
      console.error('Microphone access denied:', err);
      alert('Microphone access is required for audio recording.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="call-interface glass-card">
      <div className="ci-header">
        <h3 className="ci-title">📞 Citizen Call Simulator</h3>
        <div className="ci-status">
          <span className={`status-dot ${isProcessing ? 'warning' : 'active'}`} />
          <span>{isProcessing ? 'Processing...' : 'Ready'}</span>
        </div>
      </div>

      {/* Language & Dialect Selection */}
      <div className="ci-controls">
        <div className="ci-control-group">
          <label className="ci-label">Language</label>
          <select
            className="select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            id="language-select"
          >
            <option value="kannada">Kannada</option>
            <option value="hindi">Hindi</option>
            <option value="english">English</option>
            <option value="kannada-hindi">Kannada-Hindi Mix</option>
            <option value="kannada-english">Kannada-English Mix</option>
          </select>
        </div>
        <div className="ci-control-group">
          <label className="ci-label">Dialect</label>
          <select
            className="select"
            value={dialect}
            onChange={(e) => setDialect(e.target.value)}
            id="dialect-select"
          >
            <option value="standard">Standard Kannada</option>
            <option value="dharwad">Dharwad Kannada</option>
            <option value="mysuru">Mysuru Kannada</option>
            <option value="mangaluru">Mangaluru Kannada</option>
            <option value="havyaka">Havyaka</option>
            <option value="north-karnataka">North Karnataka</option>
          </select>
        </div>
      </div>

      {/* Text Input */}
      <div className="ci-text-input">
        <textarea
          className="textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type what the citizen says... (Kannada transliterated, Hindi, or English)"
          rows={3}
          id="citizen-text-input"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmitText();
            }
          }}
        />
        <div className="ci-text-actions">
          <button
            className="btn btn-primary"
            onClick={handleSubmitText}
            disabled={!text.trim() || isProcessing}
            id="submit-text-btn"
          >
            {isProcessing ? (
              <>
                <span className="animate-spin">⏳</span>
                Processing...
              </>
            ) : (
              <>🧠 Process with AI</>
            )}
          </button>
        </div>
      </div>

      {/* Audio Recording */}
      <div className="ci-audio">
        <div className="ci-audio-controls">
          {!isRecording ? (
            <button className="btn btn-ghost btn-lg record-btn" onClick={startRecording} id="record-btn">
              <span className="record-icon">🎙️</span>
              Record Audio
            </button>
          ) : (
            <button className="btn btn-danger btn-lg record-btn recording" onClick={stopRecording} id="stop-record-btn">
              <span className="recording-pulse" />
              Stop Recording ({recordingDuration}s)
            </button>
          )}
        </div>
      </div>

      {/* Sample Queries */}
      <div className="ci-samples">
        <h4 className="ci-samples-title">Quick Test Scenarios</h4>
        <div className="sample-grid">
          {SAMPLE_QUERIES.map((sample, i) => (
            <button
              key={i}
              className="btn btn-ghost btn-sm sample-btn"
              onClick={() => handleSampleQuery(sample)}
              title={sample.text}
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
