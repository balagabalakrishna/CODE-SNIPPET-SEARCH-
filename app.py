
import streamlit as st
from PIL import Image
import traceback
from datetime import datetime 
import os
import bcrypt
import google.generativeai as genai
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
# Add near the top (with other imports)
### new added
# REPLACE WITH:
from preprocessor import save_snippet_to_file, get_snippets_file, preprocessor  

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import json
from pathlib import Path
from utils.gpt import generate_code

  # Stops the app if not authenticate
# Set page config
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-1.5-flash')



# ===== END OF WELCOME MESSAGE =====
st.set_page_config(
    page_title="Code Nest",
    page_icon="https://s2.googleusercontent.com/s2/favicons?domain=deepmind.com",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS with new gradient
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(125% 125% at 50% 10%, #000 40%, #63e 100%);
        background-attachment: fixed;
        color: white;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, 
            #1a1a1a 0%, 
            #2d0063 100%);
        border-right: 1px solid #4a148c;
    }
    /* Card styling */
    .st-emotion-cache-1y4p8pa {
        background-color: rgba(30, 30, 30, 0.85);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #4a148c;
        color: white;
    }
    /* Text contrast */
    .st-emotion-cache-16txtl3 h1, 
    .st-emotion-cache-16txtl3 h2, 
    .st-emotion-cache-16txtl3 h3 {
        color: #b388ff; /* Light Purple */
    }
    /* General text color */
    .st-emotion-cache-16txtl3, 
    .st-emotion-cache-16txtl3 p, 
    .st-emotion-cache-16txtl3 div {
        color: white !important;
    }
     .title-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    .title-container img {
        width: 48px;
        height: 48px;
        margin-bottom: 0.5rem;
     .search-container {
        max-width: 600px;  /* Increased from 300px to allow full rounding */
        margin: 0 auto 2rem auto;
    }
    /* TARGETS THE SEARCH INPUT DIRECTLY */
    div.stTextInput>div>div>input {
        border-radius: 60px !important;
        padding: 12px 20px !important;
        border: 1px solid #4a148c !important;
        height: 46px !important;
        
        background-clip: padding-box !important;  /* Prevents background bleed */
        outline: none !important;                /* Removes focus outline artifacts */
        box-shadow: none !important;  
    }
    
    /* MAKES THE CONTAINER WIDER FOR BETTER VISIBILITY */
    div.stTextInput {
        max-width: 600px;
        margin: 0 auto;
    }
    }
    .search-container .stTextInput>div>div>input::placeholder {
        opacity: 0;
        transition: opacity 0.9s ease;
    }
    }
    .search-container .stTextInput>div>div>input:focus::placeholder,
    .search-container .stTextInput>div>div>input:hover::placeholder {
        opacity: 1;
    }
    .snippet-header {
    display: flex;
    align-items: center;
    gap: 10px;
    }
    .tag {
        display: inline-block;
        background-color: #4a148c;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .lang-icon {
        width: 24px;
        height: 24px;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("""
    <style>
        /* Sidebar specific styles */
        [data-testid="stSidebarUserContent"] {
            padding: 1rem;
        }
        
        .sidebar-section {
            margin-bottom: 1.5rem;
            padding: 0.5rem;
            border-radius: 8px;
            background: rgba(30, 30, 30, 0.3);
            border: 1px solid #4a148c;
        }
        
        .sidebar-title {
            color: #b388ff;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        
        /* Theme toggle switch */
        .theme-switch {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .theme-switch-label {
            color: #b388ff;
            font-size: 0.9rem;
        }
        
        /* Stats cards */
        .stats-card {
            background: rgba(30, 30, 30, 0.5);
            border-radius: 8px;
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border: 1px solid #4a148c;
        }
        
        .stats-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #b388ff;
        }
        
        .stats-label {
            font-size: 0.8rem;
            color: #b388ff;
            opacity: 0.8;
        }
        
        /* Tag selector */
        .stMultiSelect [data-baseweb=tag] {
            background-color: #4a148c;
            color: white;
        }
        
        /* Light mode adjustments */
        [data-testid="stAppViewContainer"][data-theme="light"] {
            background: radial-gradient(125% 125% at 50% 10%, #f5f5f5 40%, #e0d1ff 100%);
            color: #333;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-1y4p8pa {
            background-color: rgba(255, 255, 255, 0.9);
            color: #333;
            border: 1px solid #d1c4e9;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] .gradient-text,
        [data-testid="stAppViewContainer"][data-theme="light"] .gradient-subheader {
            background: linear-gradient(90deg, #7b1fa2, #4527a0);
        }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        /* Dark mode background */
        [data-testid="stAppViewContainer"][data-theme="dark"] {
            background: radial-gradient(125% 125% at 50% 10%, #000000 40%, #4b006e 100%) !important;
            background-attachment: fixed;
        }
        
        /* Light mode background */
        [data-testid="stAppViewContainer"][data-theme="light"] {
            background: radial-gradient(125% 125% at 50% 10%, #ffffff 40%, #e0d1ff 100%) !important;
            background-attachment: fixed;
        }
        
        /* Dark mode text and cards */
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-16txtl3,
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-16txtl3 p,
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-16txtl3 div,
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-1y4p8pa {
            color: white !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-1y4p8pa {
            background-color: rgba(30, 30, 30, 0.85) !important;
            border: 1px solid #4a148c !important;
        }
        
        /* Light mode text and cards */
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-16txtl3,
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-16txtl3 p,
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-16txtl3 div,
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-1y4p8pa {
            color: #333333 !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-1y4p8pa {
            background-color: rgba(255, 255, 255, 0.85) !important;
            border: 1px solid #d1c4e9 !important;
        }
        
        /* Gradient text that works in both modes */
        .gradient-text {
            background: linear-gradient(90deg, #9c7bff, #6e3eff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] .gradient-text {
            background: linear-gradient(90deg, #7b1fa2, #4527a0);
        }
        /* Light mode specific fixes */
        [data-testid="stAppViewContainer"][data-theme="light"] .gradient-text {
            background: linear-gradient(90deg, #7b1fa2, #4527a0) !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            color: transparent !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] h2 {
            color: #333333 !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] h2 .gradient-text {
            background: linear-gradient(90deg, #7b1fa2, #4527a0) !important;
        }
        
        /* Dark mode adjustments to maintain consistency */
        [data-testid="stAppViewContainer"][data-theme="dark"] h2 {
            color: white !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="dark"] h2 .gradient-text {
            background: linear-gradient(90deg, #9c7bff, #6e3eff) !important;
        }
          /* Light mode adjustments for expander titles */
    [data-testid="stAppViewContainer"][data-theme="light"] .snippet-header span {
        color: #333333 !important;
    }
    
    /* Dark mode maintain existing style */
    [data-testid="stAppViewContainer"][data-theme="dark"] .snippet-header span {
        color: white !important;
    }
            [data-testid="stAppViewContainer"] {
        background: radial-gradient(125% 125% at 50% 10%, #000 40%, #63e 100%);
        background-attachment: fixed;
        color: white;
    }
    
    /* Add the new CSS rules here - between the existing styles */
    [data-testid="stAppViewContainer"][data-theme="light"] .snippet-header span {
        color: #333333 !important;  /* Dark text for light mode */
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .snippet-header span {
        color: white !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="light"] {
        background: radial-gradient(125% 125% at 50% 10%, #fff 40%, #63e 100%) !important;
    }
    /* End of new CSS rules */
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, 
            #1a1a1a 0%, 
            #2d0063 100%);
        border-right: 1px solid #4a148c;
    }
    /* Rest of your existing CSS... */
     /* Light mode specific fixes */
        [data-testid="stAppViewContainer"][data-theme="light"] .gradient-text {
            background: linear-gradient(90deg, #7b1fa2, #4527a0) !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            color: transparent !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] h2 {
            color: #333333 !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"] h2 .gradient-text {
            background: linear-gradient(90deg, #7b1fa2, #4527a0) !important;
        }
        
        /* Dark mode adjustments to maintain consistency */
        [data-testid="stAppViewContainer"][data-theme="dark"] h2 {
            color: white !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="dark"] h2 .gradient-text {
            background: linear-gradient(90deg, #9c7bff, #6e3eff) !important;
        }
        
        /* Light mode adjustments for expander titles */
        [data-testid="stAppViewContainer"][data-theme="light"] .snippet-header span {
            color: #333333 !important;
        }
        
        /* Dark mode maintain existing style */
        [data-testid="stAppViewContainer"][data-theme="dark"] .snippet-header span {
            color: white !important;
        }
        
        /* NEW CODE STARTS HERE - Add this section */
        /* Target expander titles in light mode */
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-1hynsf2 summary,
        [data-testid="stAppViewContainer"][data-theme="light"] .st-emotion-cache-1hynsf2 summary span {
            color: #333333 !important;
        }
        
        /* Target expander titles in dark mode */
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-1hynsf2 summary,
        [data-testid="stAppViewContainer"][data-theme="dark"] .st-emotion-cache-1hynsf2 summary span {
            color: white !important;
        }
        /* NEW CODE ENDS HERE */
        
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(125% 125% at 50% 10%, #000 40%, #63e 100%);
            background-attachment: fixed;
            color: white;
        }
               /* Your existing CSS... */

        /* Light mode background replacement */
        [data-testid="stAppViewContainer"][data-theme="light"] {
            position: relative;
            background: transparent !important;
        }
        
        [data-testid="stAppViewContainer"][data-theme="light"]::before {
            content: "";
            position: absolute;
            inset: 0;
            z-index: -10;
            height: 100%;
            width: 100%;
            background: radial-gradient(125% 125% at 50% 10%, #fff 40%, #63e 100%);
        }
        
        /* Ensure content stays above the background */
        [data-testid="stAppViewContainer"] > div {
            position: relative;
        }
        
        /* Your other theme-specific styles... */
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "data/snippets.json"
# Language icons mapping

LANGUAGE_ICONS = {
    "python": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg",
    "javascript": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg",
    "typescript": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg",
    "java": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/java/java-original.svg",
    "c": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/c/c-original.svg",
    "twitter x " : "https://cdn-icons-png.flaticon.com/512/4401/4401470.png",
    "cpp": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg",
    "csharp": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg",
    "go": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg",
    "rust": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rust/rust-plain.svg",
    "ruby": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ruby/ruby-original.svg",
    "php": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg",
    "swift": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/swift/swift-original.svg",
    "kotlin": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kotlin/kotlin-original.svg",
    "scala": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/scala/scala-original.svg",
    "r": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/r/r-original.svg",
    "microsoft" : "https://cdn-icons-png.flaticon.com/512/732/732221.png",
    "google deep mid": "https://s2.googleusercontent.com/s2/favicons?domain=deepmind.com",
    "dart": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dart/dart-original.svg",
    
    "haskell": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/haskell/haskell-original.svg",
    "react": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg",
    "vue": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg",
    "angular": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/angularjs/angularjs-original.svg",
   
    "django": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/django/django-plain.svg",
    "meta ai": "https://s2.googleusercontent.com/s2/favicons?domain=meta.ai",
    "flask": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg",
    "express": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/express/express-original.svg",
    "spring": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/spring/spring-original.svg",
    "laravel": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/laravel/laravel-plain.svg",
    "rails": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/rails/rails-original.svg",
    "pandas": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg",
    "numpy": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg",
    "tensorflow": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tensorflow/tensorflow-original.svg",
    "pytorch": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pytorch/pytorch-original.svg",
    "docker": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg",
    "kubernetes": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kubernetes/kubernetes-plain.svg",
    "aws": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/amazonwebservices/amazonwebservices-original.svg",
    "azure": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/azure/azure-original.svg",
    "gcp": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg",
    "firebase": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/firebase/firebase-plain.svg",
    "sql": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg",
    "postgresql": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg",
    "mongodb": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg",
    "redis": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg",
    "html": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg",
    "css": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg",
    "sass": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sass/sass-original.svg",
    "less": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/less/less-plain-wordmark.svg",
    "bootstrap": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bootstrap/bootstrap-original.svg",
    "tailwind": "https://s2.googleusercontent.com/s2/favicons?domain=meta.ai",
    "materialize": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/materialui/materialui-original.svg",
    "graphql": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/graphql/graphql-plain.svg",
    "nodejs": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nodejs/nodejs-original.svg",
    "npm": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/npm/npm-original-wordmark.svg",
    "yarn": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/yarn/yarn-original.svg",
    "git": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg",
    "github": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg",
    "gitlab": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/gitlab/gitlab-original.svg",
    "bitbucket": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bitbucket/bitbucket-original.svg",
    "jira": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jira/jira-original.svg",
    "trello": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/trello/trello-plain.svg",
    "slack": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/slack/slack-original.svg",
    "vscode": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg",
    "vim": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vim/vim-original.svg",
    "intellij": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/intellij/intellij-original.svg",
    "eclipse": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/eclipse/eclipse-original.svg",
    "xcode": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/xcode/xcode-original.svg",
    "android": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/android/android-original.svg",
    "apple": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/apple/apple-original.svg",
    "windows": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg",
    "linux": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg",
    "ubuntu": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ubuntu/ubuntu-plain.svg",
    "debian": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/debian/debian-original.svg",
    "redhat": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redhat/redhat-original.svg",
    "centos": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/centos/centos-original.svg",
    "fedora": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fedora/fedora-original.svg",
    "raspberrypi": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/raspberrypi/raspberrypi-original.svg",
    "arduino": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/arduino/arduino-original.svg",
    "bash": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bash/bash-original.svg",
    "powershell": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/powershell/powershell-original.svg",
    "markdown": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/markdown/markdown-original.svg",
    "latex": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/latex/latex-original.svg",
    "jekyll": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jekyll/jekyll-original.svg",
    "hugo": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/hugo/hugo-original.svg",
    "gatsby": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/gatsby/gatsby-original.svg",
    "nextjs": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg",
    "nuxtjs": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nuxtjs/nuxtjs-original.svg",
    "jest": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jest/jest-plain.svg",
    "mocha": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mocha/mocha-plain.svg",
    
    "karma": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/karma/karma-original.svg",
    "selenium": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/selenium/selenium-original.svg",
    "cypress": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cypress/cypress-original.svg",
    "puppeteer": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/puppeteer/puppeteer-original.svg",
    "playwright": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/playwright/playwright-original.svg",
    "webdriverio": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/webdriverio/webdriverio-original.svg",
    "protractor": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/protractor/protractor-original.svg",
    "nightwatch": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nightwatch/nightwatch-original.svg",
    "testcafe": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/testcafe/testcafe-original.svg",
    "taiko": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/taiko/taiko-original.svg",
    "cucumber": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cucumber/cucumber-original.svg",
    "robotframework": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/robotframework/robotframework-original.svg",
    "appium": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/appium/appium-original.svg",
    "espresso": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/espresso/espresso-original.svg",
    "xcuitest": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/xcuitest/xcuitest-original.svg",
    "selendroid": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/selendroid/selendroid-original.svg",
    "calabash": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/calabash/calabash-original.svg",
    "detox": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/detox/detox-original.svg",
    "maestro": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/maestro/maestro-original.svg",
    "applitools": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/applitools/applitools-original.svg",
    "perfecto": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/perfecto/perfecto-original.svg",
    "saucelabs": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/saucelabs/saucelabs-original.svg",
    "browserstack": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/browserstack/browserstack-original.svg",
    "crossbrowsertesting": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/crossbrowsertesting/crossbrowsertesting-original.svg",
    "lambdatest": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/lambdatest/lambdatest-original.svg",
    "testingbot": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/testingbot/testingbot-original.svg",
    "headspin": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/headspin/headspin-original.svg",
    "kobiton": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/kobiton/kobiton-original.svg",
    "pcloudy": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pcloudy/pcloudy-original.svg",
    "perfectomobile": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/perfectomobile/perfectomobile-original.svg",
    "experitest": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/experitest/experitest-original.svg",
    "bitbar": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bitbar/bitbar-original.svg",
    "testobject": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/testobject/testobject-original.svg",
    "testdroid": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/testdroid/testdroid-original.svg",
    "awsdevicefarm": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/awsdevicefarm/awsdevicefarm-original.svg",
    "firebase": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/firebase/firebase-original.svg",
    "azuredevops": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/azuredevops/azuredevops-original.svg",
    "circleci": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/circleci/circleci-original.svg",
    "travisci": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/travisci/travisci-original.svg",
    "jenkins": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jenkins/jenkins-original.svg",
    "gitlabci": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/gitlabci/gitlabci-original.svg",
    "githubactions": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/githubactions/githubactions-original.svg",
     # Replace AWS icons with Amazon icon
     # Replace all AWS-related entries with Meta logo
      # Replace all AWS-related entries with Grok logo (using xAI logo as proxy)
     # Replace all AWS-related entries with Google Colab logo
    "aws":"https://www.google.com/s2/favicons?domain=aws.amazon.com",
    "amazonwebservices": "https://www.google.com/s2/favicons?domain=aws.amazon.com",
    "lambda": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/1200px-Google_Colaboratory_SVG_Logo.svg.png",
    "ec2": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/1200px-Google_Colaboratory_SVG_Logo.svg.png",
    "s3": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/1200px-Google_Colaboratory_SVG_Logo.svg.png",
    "rds": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/1200px-Google_Colaboratory_SVG_Logo.svg.png",
    "cloudwatch": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Google_Colaboratory_SVG_Logo.svg/1200px-Google_Colaboratory_SVG_Logo.svg.png",
    "jasmine": "https://s2.googleusercontent.com/s2/favicons?domain=meta.ai" ,
    # Git/GitHub
    "git": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg",
    "github": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg",
    
    
    # Prompt Engineering
    "prompt": "https://s2.googleusercontent.com/s2/favicons?domain=meta.ai",# AI icon
    "promptengineering": "https://s2.googleusercontent.com/s2/favicons?domain=meta.ai"
    
}

# ===== ADD THESE NEW CONFIGS =====
PROCESSED_DIR = "data/processed"  
EMBEDDINGS_PATH = os.path.join(PROCESSED_DIR, "embeddings.faiss")
METADATA_PATH = os.path.join(PROCESSED_DIR, "metadata.json")
TIMESTAMP_PATH = os.path.join(PROCESSED_DIR, "timestamps.txt")

# --- Helper Functions ---
def set_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = "dark"
    st.session_state.theme = "dark" if st.session_state.theme_toggle else "light"
    st._config.set_option("theme.primaryColor", "#6e3eff")
    st._config.set_option("theme.backgroundColor", "#1a1a1a" if st.session_state.theme == "dark" else "#ffffff")
    st._config.set_option("theme.secondaryBackgroundColor", "#2d0063" if st.session_state.theme == "dark" else "#e0d1ff")
    st._config.set_option("theme.textColor", "#ffffff" if st.session_state.theme == "dark" else "#333333")
# ===== LOGIN CREDENTIALS =====
# Add these right here (after other constants, before functions)

def load_snippets():
    """Load snippets from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
# --- Helper Functions ---

# Pre-hashed password for "root"

def show_sidebar(snippets):
    """Display the sidebar with theme toggle"""
    with st.sidebar:
        # Initialize theme if not set
        if 'theme' not in st.session_state:
            st.session_state.theme = "dark"
        
        # Theme toggle switch
        st.markdown('<div class="sidebar-title">Theme Settings</div>', unsafe_allow_html=True)
        current_theme = st.toggle(
            "Dark Mode",
            value=(st.session_state.theme == "dark"),
            key="theme_toggle",
            help="Switch between light and dark mode",
            on_change=lambda: setattr(st.session_state, 'theme', 
                                   "dark" if st.session_state.theme_toggle else "light")
        )
        
        # Statistics section
        st.markdown('<div class="sidebar-title">Snippet Statistics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class="stats-card">
                    <div class="stats-value">{}</div>
                    <div class="stats-label">Total Snippets</div>
                </div>
            """.format(len(snippets)), unsafe_allow_html=True)
        
        with col2:
            # Count unique languages
            languages = set(s.get('language', 'Unknown') for s in snippets)
            st.markdown("""
                <div class="stats-card">
                    <div class="stats-value">{}</div>
                    <div class="stats-label">Languages</div>
                </div>
            """.format(len(languages)), unsafe_allow_html=True)
        
        # Tag filtering section
        st.markdown('<div class="sidebar-title">Filter by Tags</div>', unsafe_allow_html=True)
        
        # Get all unique tags from snippets
        all_tags = set()
        for snippet in snippets:
            if 'tags' in snippet:
                all_tags.update(tag.lower() for tag in snippet['tags'])
        
        if all_tags:
            selected_tags = st.multiselect(
                "Select tags to filter",
                options=sorted(all_tags),
                default=[],
                key="tag_filter",
                label_visibility="collapsed"
            )
            
            # Store selected tags in session state
            st.session_state.selected_tags = selected_tags
        else:
            st.info("No tags available in snippets")
            st.session_state.selected_tags = []
        
                
        # Additional sidebar content
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; font-size: 0.8rem; color: #b388ff;">
                <p>Made by Bala Krishna</p>
                <p>v1.0.0</p>
            </div>
        """, unsafe_allow_html=True)

def filter_snippets_by_tags(snippets, tags):
    """Filter snippets by selected tags"""
    if not tags:
        return snippets
    
    return [s for s in snippets 
            if 'tags' in s and 
            any(tag.lower() in (t.lower() for t in s['tags']) 
            for tag in tags)]

# ===== ADD PREPROCESSING CLASS =====
class SnippetHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app
        
    def on_modified(self, event):
        if event.src_path.endswith(DATA_FILE):
            self.app.clear_cache_and_reload()

def get_language_icon(language=None, tags=None):
    """Return the best icon URL, with cloud fallback for AWS/cloud services."""
    if not tags and not language:
        return LANGUAGE_ICONS['default']
    
    search_terms = []
    if tags:
        search_terms.extend(str(tag).lower().strip() for tag in tags)
    if language:
        search_terms.append(str(language).lower().strip())
    
    # Priority 1: Exact matches (e.g., "aws" → AWS icon)
    for term in search_terms:
        if term in LANGUAGE_ICONS:
            return LANGUAGE_ICONS[term]
    
    # Priority 2: Cloud-related terms → Default cloud icon
    CLOUD_TERMS = ["aws", "amazonwebservices", "lambda", "cloud", "serverless", "azure", "gcp"]
    for term in search_terms:
        if term in CLOUD_TERMS:
            return LANGUAGE_ICONS["default_cloud"]
    
    # Priority 3: Partial matches (e.g., "git" in "github")
    for term in search_terms:
        for key, url in LANGUAGE_ICONS.items():
            if key in term or term in key:
                return url
    
    # Final fallback
    return LANGUAGE_ICONS['default']

def filter_snippets(snippets, search_query):
    """Search without AWS-specific logic"""
    if not search_query:
        return snippets
    
    return [s for s in snippets if 
            search_query.lower() in str(s.get('title', '')).lower() or
            search_query.lower() in str(s.get('description', '')).lower() or
            search_query.lower() in str(s.get('language', '')).lower() or
            search_query.lower() in str(s.get('code', '')).lower() or
            any(search_query.lower() in str(tag).lower() for tag in s.get('tags', []))]
def get_most_popular_snippets(snippets, search_logs):
    """Return top 5 most recently searched snippets"""
    recent_searches = search_logs[-100:]  # Consider last 100 searches
    
    # Create a dictionary to map snippet titles to their snippet objects
    title_to_snippet = {snippet['title'].lower(): snippet for snippet in snippets}
    
    # Track the most recent position for each snippet
    snippet_recency = {}
    
    # Go through search logs in reverse order (most recent first)
    for i, search in enumerate(reversed(recent_searches)):
        search_lower = search.lower()
        # Check for exact match first
        if search_lower in title_to_snippet:
            snippet_title = search_lower
            snippet_recency[snippet_title] = i  # More recent searches get lower numbers
        else:
            # Optional: if you want partial matches
            for title in title_to_snippet:
                if search_lower in title:
                    # Only update if we haven't seen this snippet yet
                    if title not in snippet_recency:
                        snippet_recency[title] = i
    
    # Sort snippets by their recency score (lower is more recent)
    # Only include snippets that were actually searched for
    searched_snippets = [s for s in snippets if s['title'].lower() in snippet_recency]
    
    return sorted(
        searched_snippets,
        key=lambda x: snippet_recency[x['title'].lower()],
    )[:5]

# Add this function near your other helper functions
def save_ai_snippet(query, code, language="python"):
    """Automatically save AI-generated snippets"""
    snippet_data = {
        "title": f"AI Generated: {query[:50]}...",  # Truncate long queries
        "description": f"Automatically generated for search: {query}",
        "code": code,
        "language": language,
        "tags": ["ai-generated", "auto-saved"],
        "created_at": datetime.datetime.now().isoformat()
    }
    
    try:
        # Get the current snippets
        snippets = load_snippets()
        snippets.append(snippet_data)
        
        # Save back to file
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(snippets, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Failed to auto-save snippet: {e}")
        return False


# UI COMPONENTS
def show_header():
    """Display the header with logo"""
    logo_path = r"C:\Users\RADHA KRISHNA\code-snippet-search\assest\logo.png"
    
    # Convert image to base64 to embed directly in HTML
    try:
        import base64
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        logo_html = f"<img src='data:image/png;base64,{encoded_string}' style='width:140px; display: block; margin: 0 auto;'>"
    except Exception as e:
        st.error(f"Logo not found! Error: {e}")
        logo_html = ""

    # Header with embedded logo and gradient styling
    st.markdown(f"""
    <style>
        .gradient-text {{
            background: linear-gradient(90deg, #63e, #0066ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            
        }}
        .header-container {{
            text-align: center;
            margin-bottom: 2rem;
        }}
    </style>
    <div class="header-container">
        {logo_html}
        <h1><span class="gradient-text">CODE NEST</span></h1>
        <p style="margin-top: 0.5rem;"><span class="gradient-text">The smart way to manage and generate code snippets</span></p>
    </div>
    """, unsafe_allow_html=True)


def show_search_bar():
    """Search bar with perfect 55px rounded corners and increased size"""
    st.markdown("""
    <style>
        /* Main container */
        div[data-testid="stTextInput"] {
            max-width: 650px !important;  /* Slightly wider */
            margin: 0 auto 1.5rem auto;  /* Added bottom margin */
        }
        
        /* BaseWeb input container */
        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            border-radius: 55px !important;
            background: rgba(30, 30, 30, 0.9) !important;  /* Darker background */
            border: 2px solid #7c4dff !important;  /* Brighter purple border */
            padding: 0 !important;
            overflow: hidden;
            height: 60px !important;  /* Increased height */
        }
        
        /* Actual input element */
        div[data-testid="stTextInput"] input {
            border-radius: 55px !important;
            height: 60px !important;  /* Matches container height */
            padding: 0 28px !important;  /* Increased padding */
            width: 100% !important;
            background: transparent !important;
            color: white !important;
            font-size: 17px !important;  /* Slightly larger font */
            
            /* Complete reset */
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }
        
        /* Focus state - more prominent */
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #9c7bff !important;
            box-shadow: 0 0 0 4px rgba(156, 123, 255, 0.3) !important;
            background: rgba(40, 40, 40, 0.9) !important;
        }
        
        /* Placeholder styling */
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 16px !important;
        }
        
        /* Search icon in placeholder */
        div[data-testid="stTextInput"] input::placeholder {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23b388ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: left center;
            padding-left: 30px !important;
        }
                
    </style>
    """, unsafe_allow_html=True)

    return st.text_input(
        "Search",
        placeholder="Search snippets...",  # Icon now in CSS
        key="enhanced_search_bar",
        label_visibility="collapsed"
    )

def display_snippet(snippet):
    """Simplified display without AWS formatting"""
    with st.container():
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <img src="{get_language_icon(snippet.get('language'), snippet.get('tags', []))}" 
                 style="width: 20px; height: 20px;">
            <span style="font-weight: bold; font-size: 1.1rem;">{snippet['title']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("", expanded=False):
            if 'description' in snippet:
                st.write(snippet['description'])
            st.code(snippet['code'], language=snippet.get('language', '').lower())
            if 'tags' in snippet:
                st.markdown("**Tags:** " + " ".join(
                    f'<span class="tag">{tag}</span>' for tag in snippet['tags']
                ), unsafe_allow_html=True)

# ===== ADD THIS NEW FUNCTION WITH YOUR OTHER UTILITY FUNCTIONS =====
def generate_deployment_setup(framework, code):
    """Generate deployment configuration for the generated code"""
    if framework == "Flask":
        return f"""
# Deployment Setup for Flask App
# 1. Install required packages:
# pip install flask gunicorn

# 2. Create app.py with your generated code

# 3. Create Procfile:
# web: gunicorn app:app

# 4. Create requirements.txt:
# flask
# gunicorn

# 5. Deploy to Heroku or similar platform
"""
    elif framework == "FastAPI":
        return f"""
# Deployment Setup for FastAPI App
# 1. Install required packages:
# pip install fastapi uvicorn[standard]

# 2. Create main.py with your generated code

# 3. Run locally with:
# uvicorn main:app --reload

# 4. For production deployment:
# pip install gunicorn
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# 5. Create requirements.txt:
# fastapi
# uvicorn[standard]
# gunicorn
"""
    return ""

# ===== ADD THESE ADDITIONAL UTILITY FUNCTIONS TOO =====
def analyze_complexity(code):
    """Analyze time and space complexity of code"""
    analysis_prompt = f"""
    Analyze the time and space complexity of this code:
    {code}
    
    Provide:
    1. Time complexity in Big O notation
    2. Space complexity in Big O notation
    3. Brief explanation of your analysis
    """
    return generate_code(analysis_prompt)

def generate_eli5_explanation(code):
    """Generate ELI5 explanation for code"""
    eli5_prompt = f"""
    Explain this code like I'm 5 years old:
    {code}
    
    Requirements:
    - Use simple language a child would understand
    - Use analogies from everyday life
    - Break down complex concepts
    - Keep it under 200 words
    """
    return generate_code(eli5_prompt)
# ===== END OF NEW UTILITY FUNCTIONS =====
def show_ai_generator():
    """Display the AI code generation section with gradient text"""
    st.markdown("---")
    
    # CSS styles
    st.markdown("""
    <style>
        /* Gradient header style */
        .gradient-subheader {
            background: linear-gradient(90deg, #FF6B6B, #6B6BFF);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        /* Header with logo */
        .header-with-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1.5rem;
        }
                  
        .header-logo {
            width: 36px;
            height: 36px;
            object-fit: contain;
        }

        /* Gradient button style */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #6e3eff, #0066ff);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            background: linear-gradient(90deg, #7c4dff, #1a7cff);
        }
        
        /* Clipboard button */
        div.stButton > button[kind="secondary"] {
            background: rgba(30, 30, 30, 0.9);
            border: 1px solid #7c4dff;
            border-radius: 8px;
            padding: 0.5rem 1rem 0.5rem 2.5rem;
            position: relative;
            color: white;
            transition: all 0.2s ease;
        }
        
        div.stButton > button[kind="secondary"]:hover {
            background: rgba(40, 40, 40, 0.9);
            border-color: #9c7bff;
        }
        
        .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #6e3eff !important;
        }
        
        div.stButton > button[kind="secondary"]::before {
            content: "📋";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1rem;
        }
        
        /* Gradient label */
        .gradient-label {
            background: linear-gradient(90deg, #6e3eff, #0066ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-size: 20px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logo
    st.markdown('''
        <div class="header-with-logo">
            <img class="header-logo" src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg">
            <h2 style="margin: 0;"><span class="gradient-subheader">AI Code Generation</span></h2>
        </div>
    ''', unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("### Generation Options")
        # Add mode selector at the top of sidebar
        mode = st.radio(
            "AI Mode",
            [" Code Generation", " Debugging Mode", " Translation Mode", "AutoPilot Builder"],
            index=0
        )
        
        snippet_type = st.selectbox(
            "Snippet Type",
            ["Function", "Class", "API Endpoint", "Algorithm", "CLI Command", "Other"],
            index=0
        )
        
        # Add debugging-specific options that only show in debug mode
        if "Debugging" in mode:
            debug_level = st.selectbox(
                "Debug Level",
                ["Basic", "Detailed", "Performance Focus"],
                index=0
            )

        # Add after your existing sidebar options
        if "AutoPilot Builder" in mode:
            st.markdown("---")
            st.markdown("#### AutoPilot Options")
            
            framework = st.selectbox(
                "Framework",
                ["Flask", "FastAPI", "Django REST", "Express.js", "Spring Boot"],
                index=0
            )
            
            include_tests = st.checkbox("Include Unit Tests", value=True)
            optimize_code = st.checkbox("Optimize & Debug", value=True)
            explain_eli5 = st.checkbox("ELI5 Explanation", value=False)
            complexity_analysis = st.checkbox("Complexity Analysis", value=True)
            
            # Optional deployment option
            if framework in ["Flask", "FastAPI"]:
                one_click_deploy = st.checkbox("Generate Deployment Setup", value=False)

    with st.form("ai_code_generation"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Dynamic prompt based on mode
            if "Debugging" in mode:
                prompt_label = "Describe or paste the error you're encountering:"
                prompt_placeholder = "Example: 'Getting NoneType error when processing user input'"
            elif " Translation Mode" in mode:
                prompt_label = "Paste the code you want to translate:"
                prompt_placeholder = "Examples: 'Convert this to Java: <code>' or 'Translate this TensorFlow 1.x to 2.x: <code>'"
            elif "AutoPilot Builder" in mode:
                prompt_label = "Tell me what code you want to Automate:"
                prompt_placeholder = "Describe your task: e.g., 'Plot a graph from a CSV file' or 'Connect to a database'"
            else:
                prompt_label = "Describe what you want to generate:"
                prompt_placeholder = "Example: 'Create a function to calculate factorial'"
                
            st.markdown(f'<p class="gradient-label">{prompt_label}</p>', unsafe_allow_html=True)
            prompt = st.text_area(
                "",
                placeholder=prompt_placeholder,
                height=90,
                label_visibility="collapsed"
            )
        
        with col2:
            # MOVE LANGUAGE SELECTBOX HERE - OUTSIDE ALL CONDITIONAL BLOCKS
            language = st.selectbox(
                "Language",
                ["Python", "JavaScript", "TypeScript", "Java", "Go", "C++", "Other"],
                index=0
            )
            
            if "Debugging" in mode:
                debug_type = st.selectbox(
                    "Debug Action",
                    ["Find Errors", "Fix Errors", "Optimize", "Explain Errors"],
                    index=0
                )
            elif " Translation Mode" in mode:
                # Translation mode options
                from_lang = st.selectbox(
                    "From Language",
                    ["Python", "Java", "JavaScript", "C++", "Go", "TypeScript"],
                    index=0
                )
                to_lang = st.selectbox(
                    "To Language",
                    ["Python", "Java", "JavaScript", "C++", "Go", "TypeScript"],
                    index=1  # Default to Python as target
                )
            elif "AutoPilot Builder" in mode:
                complexity = st.select_slider(
                    "Code Complexity",
                    options=["Simple", "Intermediate", "Advanced", "Production"],
                    value="Intermediate"
                )
                framework = st.selectbox(
                    "Framework (optional)",
                    ["Any", "Django", "Flask", "React", "Express.js", "Spring", "None"],
                    index=0
                )
                purpose = st.selectbox(
                    "Primary Purpose",
                    ["Automation", "Data Analysis", "Web API", "Script", "CLI Tool", "Web Scraping","other"],
                    index=0
                )
            else:
                # Original code generation options - ONLY EXPLANATION TYPE REMAINS HERE
                explanation_type = st.selectbox(
                    "Explanation",
                    ["None", "Line-by-line", "Detailed", "Simple"],
                    index=0
                )
            
        
        # Dynamic button text
        button_text = "Debug Code" if "Debugging" in mode else (
            "Translate Code" if " Translation Mode" in mode else "Generate Code"
        )
        generate_clicked = st.form_submit_button(button_text)
        
        if generate_clicked:
            if not prompt.strip():
                st.error("Please enter your request first!")
            else:
                with st.spinner(f"{button_text}..."):
                    try:
                        if "Debugging" in mode:
                            full_prompt = f"""
                            Debug this {language} code:
                            Error Type: {debug_type}
                            
                            Problem Description:
                            {prompt}
                            
                            Please:
                            1. Identify the issue
                            2. Provide fixed code
                            3. Explain the solution
                            """
                        elif " Translation Mode" in mode:
                            full_prompt = f"""
                            Translate this {from_lang} code to {to_lang}:
                            {prompt}
                            
                            Provide only the translated code with brief comments.
                            Maintain all functionality and use idiomatic {to_lang} style.
                            """
                        # ===== ADD AUTOPILOT BUILDER MODE HERE =====
                        elif "AutoPilot Builder" in mode:
                            full_prompt = f"""
                            Create a complete {framework} application for: {prompt}
                            
                            Requirements:
                            - Generate complete boilerplate code
                            - Include all necessary routes and CRUD operations
                            - Use production-ready patterns and best practices
                            - Include proper error handling
                            {"- Generate comprehensive unit tests" if include_tests else ""}
                            {"- Analyze time and space complexity" if complexity_analysis else ""}
                            {"- Provide ELI5 (Explain Like I'm 5) explanation" if explain_eli5 else ""}
                            {"- Include deployment configuration" if one_click_deploy else ""}
                            
                            Please structure the response with:
                            1. Complete implementation code
                            2. Brief explanation of architecture
                            {"3. Complexity analysis" if complexity_analysis else ""}
                            {"4. Unit tests" if include_tests else ""}
                            {"5. ELI5 explanation" if explain_eli5 else ""}
                            {"6. Deployment instructions" if one_click_deploy else ""}
                            """
                        # ===== END OF AUTOPILOT BUILDER MODE ADDITION =====
                        else:
                            full_prompt = f"Create a {language} {snippet_type}: {prompt}"
                        
                        generated_code = generate_code(full_prompt)
                        st.session_state.generated_code = generated_code
                        st.session_state.current_language = to_lang if " Translation Mode" in mode else language
                        st.session_state.mode = mode
                        
                        ### ADD AUTO-SAVE FUNCTIONALITY HERE ###
                        if st.session_state.get('auto_save', True):  # Default to True if not set
                            if save_ai_snippet(
                                prompt,
                                generated_code,
                                st.session_state.current_language
                            ):
                                st.toast("✨ Snippet auto-saved for future reference!", icon="💾")
                        ### END OF AUTO-SAVE ADDITION ###
                         # ===== ADD AUTOPILOT OPTIMIZATION LOGIC HERE =====
                # If in AutoPilot mode and optimization is enabled
                        if "AutoPilot Builder" in mode and optimize_code:
                            with st.spinner("🔧 Optimizing and debugging..."):
                                optimization_prompt = f"""
                                Optimize and debug this code:
                                {generated_code}
                                
                                Please:
                                1. Identify potential issues or inefficiencies
                                2. Suggest and implement optimizations
                                3. Ensure production readiness
                                4. Maintain all functionality
                                """
                                
                                optimized_code = generate_code(optimization_prompt)
                                st.session_state.generated_code = optimized_code
                                st.toast("✅ Code optimized!", icon="🔧")
                        # ===== END OF AUTOPILOT OPTIMIZATION LOGIC =====
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display results
    if "generated_code" in st.session_state:
        st.markdown("---")
        if "Debugging" in st.session_state.mode:
            st.markdown(f'<p class="gradient-subheader">Debugging Results</p>', unsafe_allow_html=True)
        elif " Translation Mode" in st.session_state.mode:
            st.markdown(f'<p class="gradient-subheader">Translated {st.session_state.current_language} Code</p>',
                    unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="gradient-subheader">Generated {st.session_state.current_language} Code</p>', 
                    unsafe_allow_html=True)
        
        st.code(st.session_state.generated_code, 
                language=st.session_state.current_language.lower())
        
        # ===== ADD AUTOPILOT BUILDER SPECIFIC DISPLAY LOGIC HERE =====
        if "AutoPilot Builder" in st.session_state.mode:
            st.markdown(f'<p class="gradient-subheader">AutoPilot Generated {framework} Application</p>', unsafe_allow_html=True)
            
            # Add deployment instructions if requested
            if one_click_deploy:
                deployment_instructions = generate_deployment_setup(framework, st.session_state.generated_code)
                with st.expander("🚀 Deployment Instructions"):
                    st.code(deployment_instructions)
        
        # ===== ADD COMPLEXITY ANALYSIS AND ELI5 EXPANDERS HERE =====
        if "AutoPilot Builder" in st.session_state.mode:
            if complexity_analysis:
                with st.expander("📊 Complexity Analysis"):
                    complexity = analyze_complexity(st.session_state.generated_code)
                    st.write(complexity)
            
            if explain_eli5:
                with st.expander("🧒 ELI5 Explanation"):
                    explanation = generate_eli5_explanation(st.session_state.generated_code)
                    st.write(explanation)
        # ===== END OF AUTOPILOT BUILDER DISPLAY ADDITIONS =====
        
        if st.button("📋 Copy to Clipboard", key="copy_button"):
            try:
                import pyperclip
                pyperclip.copy(st.session_state.generated_code)
                st.toast("Code copied!", icon="✅")
            except ImportError:
                st.warning("pyperclip not installed. Install with: pip install pyperclip")

    # Footer container
    footer_container = st.container()
    with footer_container:
        st.markdown("---")   
        st.caption(
            "This project is not affiliated with or endorsed by any organization.<br>"
            "All the logos used in the project are just for experimental purposes.<br>"
            "Generated code should be reviewed before use in production environments.",
            unsafe_allow_html=True
        )
# ===== ADD THE ENHANCED CLASS HERE =====


# --- Main App ---
# --- Main App ---
def main():
    
    
    # ===== ORIGINAL MAIN CONTENT =====
    # Keep all your existing code below exactly as is
    if 'search_logs' not in st.session_state:
        st.session_state.search_logs = []
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    
    snippets = load_snippets()
    

      # ===== ADD NLP INITIALIZATION HERE =====
   

    
    # Show sidebar with theme toggle and filters
    show_sidebar(snippets)
    


    # Apply theme settings
    if 'theme' in st.session_state:
        if st.session_state.theme == "dark":
            st.markdown('<style>[data-testid="stAppViewContainer"] {background: radial-gradient(125% 125% at 50% 10%, #000 40%, #63e 100%);}</style>', unsafe_allow_html=True)
        else:
            st.markdown('<style>[data-testid="stAppViewContainer"] {background: radial-gradient(125% 125% at 50% 10%, #f5f5f5 40%, #e0d1ff 100%);}</style>', unsafe_allow_html=True)
    
    show_header()

    # ===== ADD SEMANTIC SEARCH INITIALIZATION HERE =====
   
    # ===== END OF SEMANTIC SEARCH INIT =====

   
    # Create search value that combines tags and search query
    if st.session_state.selected_tags:
        tag_display = ", ".join(st.session_state.selected_tags)
        if st.session_state.search_query and not st.session_state.search_query.startswith(tag_display):
            search_value = f"{tag_display}, {st.session_state.search_query}"
        else:
            search_value = tag_display
    else:
        search_value = st.session_state.search_query
    

# Apply your beautiful search bar design
    st.markdown("""
    <style>
        /* Main container */
        div[data-testid="stTextInput"] {
            max-width: 650px !important;
            margin: 0 auto 1.5rem auto;
        }
        
        /* BaseWeb input container */
        div[data-testid="stTextInput"] div[data-baseweb="input"] {
            border-radius: 55px !important;
            background: rgba(30, 30, 30, 0.9) !important;
            border: 2px solid #7c4dff !important;
            padding: 0 !important;
            overflow: hidden;
            height: 60px !important;
        }
        
        /* Actual input element */
        div[data-testid="stTextInput"] input {
            border-radius: 55px !important;
            height: 60px !important;
            padding: 0 28px !important;
            width: 100% !important;
            background: transparent !important;
            color: white !important;
            font-size: 17px !important;
            
            /* Complete reset */
            -webkit-appearance: none !important;
            -moz-appearance: none !important;
            appearance: none !important;
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }
        
        /* Focus state - more prominent */
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
            border-color: #9c7bff !important;
            box-shadow: 0 0 0 4px rgba(156, 123, 255, 0.3) !important;
            background: rgba(40, 40, 40, 0.9) !important;
        }
        
        /* Placeholder styling */
        div[data-testid="stTextInput"] input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
            font-size: 16px !important;
        }
        
        /* Search icon in placeholder */
        div[data-testid="stTextInput"] input::placeholder {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23b388ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: left center;
            padding-left: 30px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Display the search bar with your design
    search_query = st.text_input(
        "Search",
        value=st.session_state.get('search_query', ''),  # Changed: Use session state as source of truth,
        key="unique_search_bar_key",
        placeholder="Search snippets or select tags to filter...",
        label_visibility="collapsed"
    )
    
    # Update the search state
    # Update the search state
    if search_query != st.session_state.get('search_query', ''):  # [CHANGED] Compare against session state
        if st.session_state.selected_tags:
            tag_display = ", ".join(st.session_state.selected_tags)
            if search_query.startswith(tag_display):
                # User added text after tags
                additional_query = search_query[len(tag_display):].strip(", ").strip()
                st.session_state.search_query = additional_query
            else:
                # User replaced the tags with new search
                st.session_state.search_query = search_query
                st.session_state.selected_tags = []
        else:
            # Regular search case
            st.session_state.search_query = search_query
        st.rerun()  # [ADDED] Force immediate update

    # First filter by tags if any are selected
    if st.session_state.selected_tags:
        filtered_snippets = filter_snippets_by_tags(snippets, st.session_state.selected_tags)
    else:
        filtered_snippets = snippets
    current_query = st.session_state.get('search_query', '')  # [CHANGED] Get from session state

    # Then apply additional search filtering if there's a query
    if current_query:  # [CHANGED] Use the current_query variable
        filtered_snippets = filter_snippets(filtered_snippets, current_query)

    # [CHANGED] Moved logging block here for better organization
    if current_query and current_query not in st.session_state.search_logs:
        st.session_state.search_logs.append(current_query)  # [CHANGED] Use current_query
    elif st.session_state.selected_tags:
        tag_search = ", ".join(st.session_state.selected_tags)
        if tag_search not in st.session_state.search_logs:
            st.session_state.search_logs.append(tag_search)

    # Display the appropriate content based on filters
    # Display the appropriate content based on filters
    if current_query or st.session_state.selected_tags:
        # First show keyword results
        if filtered_snippets:
            st.subheader(f"🔍 Keyword Matches ({len(filtered_snippets)})")
            for snippet in filtered_snippets:
                display_snippet(snippet)
    
        
         # ===== ADD THE NEW SEMANTIC SEARCH BLOCK RIGHT HERE =====
    # (Replace any existing semantic search code with the new version below)
    if current_query:
        with st.spinner('🔮 Finding similar code...'):
            try:
                results = preprocessor.search(current_query, top_k=3)
                unique_results = [s for s in results if s not in filtered_snippets]
                
                if unique_results:
                    st.subheader("🧠 Semantic Matches")
                    for snippet in unique_results:
                        display_snippet(snippet)
            except Exception as e:
                st.warning(f"Semantic search unavailable: {str(e)}")
    # ===== END OF NEW BLOCK =====
    # ===== ADD THE OPTIONAL GENERATOR EXPANDER RIGHT HERE =====
    if current_query:  # Only show if there's an active query
        with st.expander("💡 Not finding what you need? Generate alternative solutions"):
            st.markdown("""
            <style>
                .gradient-generate-btn {
                    background: linear-gradient(90deg, #FF6B6B, #6B6BFF) !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 8px !important;
                    padding: 0.5rem 1rem !important;
                    font-weight: 600 !important;
                    transition: all 0.2s ease !important;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
                    width: 100% !important;
                }
                
                .gradient-generate-btn:hover {
                    transform: translateY(-1px) !important;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
                    background: linear-gradient(90deg, #FF7B7B, #7B7BFF) !important;
                }
                
                .gradient-save-btn {
                    background: rgba(30, 30, 30, 0.9) !important;
                    border: 1px solid #7c4dff !important;
                    border-radius: 8px !important;
                    padding: 0.5rem 1rem !important;
                    color: white !important;
                    transition: all 0.2s ease !important;
                    width: 100% !important;
                    margin-top: 0.5rem !important;
                }
                
                .gradient-save-btn:hover {
                    background: rgba(40, 40, 40, 0.9) !important;
                    border-color: #9c7bff !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Generate Alternative with Gemini", 
                        key="generate_alt_btn",
                        help="Generate a different solution using Gemini AI"):
                with st.spinner("🧠 Gemini is generating alternatives..."):
                    try:
                        prompt = f"""
                        Create a clean, production-ready code solution for: "{current_query}"
                        - Different approach from previous results
                        - Production-ready code
                        - With brief explanation
                        - Provide only the essential code (no extra text)
                        - Specify the programming language
                        """
                        
                        response = gemini_model.generate_content(prompt)
                        ai_code = response.text

                        st.success("🔮 Alternative solution:")
                        st.markdown("---")
                        st.markdown(ai_code)
                        
                            # Auto-save the alternative
                        if save_ai_snippet(
                            f"Alternative for: {current_query}",
                            ai_code,
                            "python"  # Default language, adjust as needed
                        ):
                            st.toast("✨ Alternative snippet auto-saved!", icon="💾")
                    
                        
                    except Exception as e:
                        st.error(f"🚫 Alternative generation failed: {str(e)}")
# ===== END OF ADDED CODE =====
    else:
        st.markdown("""
        <style>
            .gradient-text {
                background: linear-gradient(90deg, #63e, #0066ff);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                display: inline;
            }
        </style>
        <h2><span class="gradient-text">Recently Searched Snippets</span></h2>
        """, unsafe_allow_html=True)
        
        popular_snippets = get_most_popular_snippets(snippets, st.session_state.search_logs)
        for snippet in popular_snippets:
            display_snippet(snippet)

        # ===== ADD CAROUSEL HERE =====
        

                # ===== ADD CAROUSEL HERE =====
        logos = [
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linux/linux-original.svg","name": "Python Two Sum" },
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/ubuntu/ubuntu-plain.svg","name": "Python Two Sum" },
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/go/go-original.svg","name": "Python Two Sum"},
            {"url":  "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/azure/azure-original.svg","name": "Python Two Sum"},
            {"url":  "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jira/jira-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/xcode/xcode-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg","name": "Python Two Sum"},
            {"url":  "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/cplusplus/cplusplus-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jenkins/jenkins-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/swift/swift-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg","name": "Python Two Sum"},
            {"url": "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg","name": "Python Two Sum"}
            
        ]

        logo_set = logos * 4
        logo_width = 100
        logo_height = 55
        item_width = 170

        html_code = f"""
        <style>
        .carousel-outer-container {{
            width: 100%;
            overflow: hidden;
            position: relative;
            margin: 30px 0 50px 0;
        }}
        
        .carousel-container {{
            width: 100%;
            padding: 20px 0;
            background: linear-gradient(90deg, 
                        rgba(45, 0, 99, 0.9) 0%, 
                        rgba(110, 62, 255, 0.7) 50%, 
                        rgba(45, 0, 99, 0.9) 100%);
            border-top: 1px solid #6e3eff;
            border-bottom: 1px solid #6e3eff;
        }}
        
        .carousel-track {{
            display: flex;
            align-items: center;
            width: calc({item_width}px * {len(logo_set)});
            animation: scroll-left 45s linear infinite;
            will-change: transform; 
        }}
        
        .carousel-item {{
            min-width: {item_width - 30}px;
            margin: 0 15px;
            padding: 10px;
            opacity: 0.9;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            background: rgba(26, 26, 26, 0.7);
            border-radius: 8px;
            box-sizing: border-box;
            backface-visibility: hidden;
        }}
        
        .carousel-item:hover {{
            transform: scale(1.15);  
            box-shadow: 0 0 20px rgba(110, 62, 255, 0.8);  
            transition: all 0.4s ease;  
        }}
        
        .carousel-logo {{
            width: {logo_width}px;
            height: {logo_height}px;
            object-fit: contain;
        }}
        
        .carousel-name {{
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            font-weight: 500;
            text-align: center;
            width: 100%;
            white-space: normal;
            word-break: break-word;
            padding: 0 5px;
        }}

        @keyframes scroll-left {{
            0% {{
            transform: translateX(0);
            }}
            100% {{
            transform: translateX(calc(-{item_width}px * {len(logos)/2}));
            }}
        }}
        </style>

        <div class="carousel-outer-container">
        <div class="carousel-container">
            <div class="carousel-track">
            {"".join(
                f'<div class="carousel-item">'
                f'<img src="{logo["url"]}" class="carousel-logo" alt="{logo["name"]}"/>'
                f'<div class="carousel-name">{logo["name"]}</div>'
                f'</div>' 
                for logo in logo_set
            )}
            </div>
        </div>
        </div>
        """

        st.markdown(html_code, unsafe_allow_html=True)
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        # ===== END OF CAROUSEL CODE =====

            
    
    # Show the AI code generator section
    show_ai_generator()
   
if __name__ == "__main__":
    main()