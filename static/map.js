window.onload = function() {
  if (!window.ISSUES) return;
  var issues = window.ISSUES;
  var map = L.map('map').setView([30.7333, 76.7794], 12); // Chandigarh default
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Add marker clustering
  var markers = L.markerClusterGroup ? L.markerClusterGroup() : null;
  var markerList = [];
  var bounds = [];

  function showIssueDetails(issue) {
    var d = issue;
    var html = '<h4>' + d.title + '</h4>';
    if (d.image_url) html += '<img src="' + d.image_url + '" style="max-width:100%;border-radius:8px;margin-bottom:0.5em;">';
    html += '<p><b>Status:</b> ' + d.status + '</p>';
    html += '<p><b>Votes:</b> ' + d.votes + '</p>';
    html += '<p><b>Location:</b> ' + d.location + '</p>';
    if (d.description) html += '<p>' + d.description + '</p>';
    document.getElementById('issue-details').innerHTML = html;
  }

  issues.forEach(function(issue) {
    if (issue.coordinates) {
      var marker = L.marker(issue.coordinates);
      marker.issueData = issue;
      marker.on('click', function(e) {
        showIssueDetails(issue);
        e.originalEvent && e.originalEvent.stopPropagation && e.originalEvent.stopPropagation();
      });
      markerList.push(marker);
      bounds.push(issue.coordinates);
      if (markers) markers.addLayer(marker);
      else marker.addTo(map);
    }
  });

  if (markers && markerList.length > 0) {
    map.addLayer(markers);
    var group = new L.featureGroup(markerList);
    map.fitBounds(group.getBounds().pad(0.2));
  } else if (markerList.length > 0) {
    var group = new L.featureGroup(markerList);
    map.fitBounds(group.getBounds().pad(0.2));
  }

  // Reset sidebar when clicking on map (not on marker)
  map.on('click', function() {
    document.getElementById('issue-details').innerHTML = 'Click a marker to see details.';
  });
};
