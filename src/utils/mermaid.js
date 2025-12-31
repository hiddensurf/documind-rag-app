import mermaid from 'mermaid';

export const initializeMermaid = () => {
  mermaid.initialize({ 
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    logLevel: 'debug',
    themeVariables: {
      primaryColor: '#a855f7',
      primaryTextColor: '#fff',
      primaryBorderColor: '#7c3aed',
      lineColor: '#c084fc',
      secondaryColor: '#1e1e1e',
      tertiaryColor: '#2a2a2a',
      background: '#171717',
      mainBkg: '#212121',
      secondBkg: '#2a2a2a',
      nodeBorder: '#7c3aed',
      clusterBkg: '#2a2a2a',
      clusterBorder: '#7c3aed',
      titleColor: '#fff',
      edgeLabelBackground: '#2a2a2a',
      nodeTextColor: '#fff'
    },
    flowchart: {
      htmlLabels: true,
      curve: 'basis',
      padding: 15
    }
  });
};

export const renderMermaid = async (element, code) => {
  try {
    console.log('Starting Mermaid render...');
    console.log('Code to render:', code);
    
    // Clear previous content
    element.innerHTML = '';
    
    // Clean up the code
    let cleanCode = code.trim();
    
    // Remove markdown code blocks if present
    cleanCode = cleanCode.replace(/```mermaid\n?/g, '').replace(/```\n?/g, '');
    cleanCode = cleanCode.trim();
    
    console.log('Cleaned code:', cleanCode);
    
    // Validate it starts with a graph type
    const validStarts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'journey', 'gantt', 'pie'];
    const hasValidStart = validStarts.some(start => cleanCode.startsWith(start));
    
    if (!hasValidStart) {
      console.log('Adding graph TD prefix');
      cleanCode = 'graph TD\n' + cleanCode;
    }
    
    // Create a unique ID
    const id = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    console.log('Using ID:', id);
    
    // Render using mermaid.render
    const { svg } = await mermaid.render(id, cleanCode);
    
    console.log('Render successful, inserting SVG');
    element.innerHTML = svg;
    
    return true;
  } catch (error) {
    console.error('Mermaid rendering error:', error);
    console.error('Error details:', {
      message: error.message,
      str: error.str,
      hash: error.hash
    });
    
    // Show detailed error
    element.innerHTML = `
      <div class="p-6 text-center space-y-4">
        <div class="text-red-500 mb-2">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <p class="text-red-500 font-semibold">Failed to Render Diagram</p>
        <p class="text-sm text-gray-500 dark:text-gray-400">${error.message}</p>
        <details class="mt-4 text-left">
          <summary class="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-2">
            View Diagram Code
          </summary>
          <pre class="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded text-xs overflow-auto max-h-60 text-left">${code}</pre>
        </details>
        <button 
          onclick="navigator.clipboard.writeText(\`${code.replace(/`/g, '\\`')}\`)" 
          class="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg text-sm"
        >
          Copy Code to Clipboard
        </button>
      </div>
    `;
    
    return false;
  }
};

export default mermaid;
