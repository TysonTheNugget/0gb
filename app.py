<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>0GB Back End</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: auto; }
        textarea, input { width: 100%; margin-bottom: 10px; }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }
        .image-grid img { width: 100%; cursor: pointer; }
        .image-grid img.selected { border: 2px solid blue; }
        button { margin-right: 10px; margin-bottom: 10px; padding: 5px 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>0GB Back End</h1>
        
        <div>
            <label for="addresses">Bitcoin Addresses (one per line):</label>
            <textarea id="addresses" rows="5"></textarea>
        </div>

        <div>
            <label for="fromDate">From Date (optional):</label>
            <input type="date" id="fromDate">
        </div>

        <div>
            <label for="toDate">To Date (optional):</label>
            <input type="date" id="toDate">
        </div>

        <div>
            <button onclick="fetchInscriptions()">Fetch Inscriptions</button>
            <button onclick="deleteSelected()">Delete Selected</button>
            <button onclick="saveRemaining()">Save Remaining</button>
            <button onclick="goToImageLink()">Go to Image Link</button>
        </div>

        <div>
            <h2>Held Inscription Images (Click to Select, Delete to Remove):</h2>
            <button onclick="selectAll('held-images')">Select All</button>
            <div id="held-images" class="image-grid"></div>
        </div>

        <div>
            <h2>Transferred Inscription Images (Click to Select, Delete to Remove):</h2>
            <button onclick="selectAll('transferred-images')">Select All</button>
            <div id="transferred-images" class="image-grid"></div>
        </div>

        <div>
            <h2>Results (JSON):</h2>
            <pre id="results"></pre>
        </div>
    </div>

    <script>
        function selectAll(containerId) {
            const container = document.getElementById(containerId);
            const images = container.getElementsByTagName('img');
            for (let img of images) {
                img.classList.toggle('selected');
            }
        }

        // Existing JavaScript functions (assumed unchanged from original implementation)
        async function fetchInscriptions() {
            const addresses = document.getElementById('addresses').value;
            const fromDate = document.getElementById('fromDate').value;
            const toDate = document.getElementById('toDate').value;
            
            const response = await fetch('/fetch_inscriptions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ addresses, from_date: fromDate, to_date: toDate })
            });
            
            const results = await response.json();
            document.getElementById('results').textContent = JSON.stringify(results, null, 2);
            
            // Example: Populate image grids (adjust based on your actual API response)
            Object.keys(results).forEach(address => {
                const held = results[address].held;
                const transferred = results[address].transferred;
                
                if (Array.isArray(held)) {
                    held.forEach(id => addImage('held-images', id));
                }
                if (Array.isArray(transferred)) {
                    transferred.forEach(id => addImage('transferred-images', id));
                }
            });
        }

        function addImage(containerId, inscriptionId) {
            const container = document.getElementById(containerId);
            const img = document.createElement('img');
            img.src = `https://ordiscan.com/inscription/${inscriptionId}`; // Adjust URL as needed
            img.onclick = () => img.classList.toggle('selected');
            container.appendChild(img);
        }

        function deleteSelected() {
            ['held-images', 'transferred-images'].forEach(containerId => {
                const container = document.getElementById(containerId);
                const images = container.getElementsByClassName('selected');
                while (images.length > 0) {
                    images[0].remove();
                }
            });
        }

        function saveRemaining() {
            // Implementation as per original
        }

        function goToImageLink() {
            // Implementation as per original
        }
    </script>
</body>
</html>