document.addEventListener('DOMContentLoaded', function () {
    const attackBtn = document.getElementById('attack-btn');
    const combatLog = document.getElementById('combat-log');
    const hero1Life = document.getElementById('hero1-life');
    const hero2Life = document.getElementById('hero2-life');
    const hero1 = document.querySelector('hero1-name');

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

    function updateLife(defender, life) {
        if (defender === hero1) {
            hero1Life.textContent = life;
        } else {
            hero2Life.textContent = life;
        }
    }

    function performAttack(attackerId) {
        return fetch('/App/combat/attack/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                attacker: attackerId
            })
        })
            .then(response => {
                if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
                return response.json();
            });
    }

    function autoCombat() {
        if (!isAuthenticated) return;

        const hero1Id = document.querySelector('.hero1-stats').dataset.heroId;
        const hero2Id = document.querySelector('.hero2-stats').dataset.heroId;
        let currentAttacker = hero1Id;

        function nextAttack() {
            performAttack(currentAttacker)
                .then(data => {
                    if (data.finished) {
                        combatLog.innerHTML += `<p class="winner">${data.message}</p>`;
                        attackBtn.disabled = true;
                        setTimeout(() => {
                            window.location.href = '/App/hero_list/';
                        }, 3000);
                        return;
                    }
                    else if (data.missed) {
                        combatLog.innerHTML += `<p class="missed">${data.attacker} rate son attaque!</p>`;
                    } else {
                        combatLog.innerHTML += `<p class="hit">${data.attacker} inflige ${data.damage} dégâts à ${data.defender}!</p>`;
                        updateLife(data.defender, data.defender_life);
                    }

                    combatLog.scrollTop = combatLog.scrollHeight;

                    currentAttacker = currentAttacker === hero1Id ? hero2Id : hero1Id;
                    setTimeout(nextAttack, 1000);
                })
                .catch(error => {
                    console.error('Erreur:', error);
                    combatLog.innerHTML += `<p class="error">Erreur durant le combat</p>`;
                });
        }

        nextAttack();
    }

    attackBtn.addEventListener('click', function () {
        isAuthenticated = true;
        attackBtn.disabled = true;
        combatLog.innerHTML = '<p class="start">Le combat commence!</p>';
        autoCombat();
    });
});