document.addEventListener('DOMContentLoaded', function() {
    const attackBtn = document.getElementById('attack-btn');
    const combatLog = document.getElementById('combat-log');
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    attackBtn.addEventListener('click', function() {
        const attackerId = this.dataset.attacker;
        
        fetch('/combat/attack/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                attacker: attackerId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.finished) {
                combatLog.innerHTML += `<p class="winner">${data.message}</p>`;
                attackBtn.disabled = true;
            } else if (data.missed) {
                combatLog.innerHTML += `<p class="missed">L'attaque a échoué!</p>`;
            } else {
                combatLog.innerHTML += 
                    `<p class="hit">${data.attacker} inflige ${data.damage} dégâts à ${data.defender}</p>`;
                document.getElementById(`${data.defender}-life`).textContent = data.defender_life;
            }
            combatLog.scrollTop = combatLog.scrollHeight;
        });
    });
});