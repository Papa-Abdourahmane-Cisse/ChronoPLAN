import streamlit as st
import streamlit.components.v1 as components

# Inject custom HTML and JavaScript
components.html("""
    <div id="parent-id">
        <div id="child-id">Child Node</div>
    </div>
    <script>
        // Ensure that the parent and child nodes are correctly identified
        const parentNode = document.getElementById('parent-id');
        const childNode = document.getElementById('child-id');

        if (parentNode && childNode && parentNode.contains(childNode)) {
            parentNode.removeChild(childNode);
        } else {
            console.error('Child node is not a child of the parent node or does not exist.');
        }
    </script>
""", height=200)
