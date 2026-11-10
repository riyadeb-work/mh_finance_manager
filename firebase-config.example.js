/**
 * firebase-config.example.js
 *
 * Template for firebase-config.js for MH Wallet — SAFE to commit.
 *
 * Instructions:
 *   1. Copy this file: cp firebase-config.example.js firebase-config.js
 *   2. Replace every placeholder below with your actual Firebase values.
 *      Find them in the Firebase console → Project Settings → Your apps.
 *   3. Restrict the API key in Google Cloud Console:
 *      APIs & Services → Credentials → HTTP referrers & API restrictions.
 *   4. Never commit firebase-config.js (it is in .gitignore).
 */

window.FIREBASE_CONFIG = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT_ID.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT_ID.firebasestorage.app",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId:             "YOUR_APP_ID"
};

