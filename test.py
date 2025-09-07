import streamlit as st

# Set theme colors
st._config.set_option("theme.primaryColor", "#6e3eff")
st._config.set_option("theme.backgroundColor", "#1a1a1a")
st._config.set_option("theme.secondaryBackgroundColor", "#2d0063")
st._config.set_option("theme.textColor", "#ffffff")


st.markdown("---")

logos = [
    {"url": "https://framerusercontent.com/images/cI2KTiTunRChu9izYs5bS0Ahbk4.svg", "name": "Python Two Sum"},
    {"url": "https://framerusercontent.com/images/FiH2Qz1PPpnj4cXfzbk1jqhvu40.svg", "name": "Python Selection Sort"},
    {"url": "https://framerusercontent.com/images/M5bwSbU2NMPvtY5nxJeLdsW6o.svg", "name": "React Web Module"},
    {"url": "https://framerusercontent.com/images/nXnD26ULduZmWqo8Zyc2LuMs8k.svg", "name": "HTML Elements"},
]

# Slightly reduced repetition
logo_set = logos * 4 # Changed from 10 to 8
logo_width = 100
logo_height = 55
item_width = 170  # Adjusted width

html_code = f"""
<style>
  .carousel-container {{
    margin: 30px -15% 50px -15%;  /* Reduced side extension */
    width: 130%;  /* Slightly wider than container */
    overflow: hidden;
    position: relative;
  }}
  
  .carousel {{
    display: flex;
    padding: 20px 0;
    width: 100%;
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
    animation: scroll-left 30s linear infinite;;
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
    white-space: normal;  /* Changed from nowrap to normal */
    word-break: break-word;  /* Added to handle long words */
    padding: 0 5px;
  }}

  @keyframes scroll-left {{
    0% {{
      transform: translateX(0);
    }}
    100% {{
      transform: translateX(calc(-{item_width}px * {len(logos)}));
    }}
  }}
</style>

<div class="carousel-container">
  <div class="carousel">
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


















  

  
  
