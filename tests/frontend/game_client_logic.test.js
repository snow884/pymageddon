const { test, describe } = require('node:test');
const assert = require('node:assert');

// Health bar texture threshold helper
function getHealthBarTexture(hp) {
    if (hp <= 20) {
        return "../../static/other/health_bar_red.png";
    }
    if (hp > 20 && hp <= 50) {
        return "../../static/other/health_bar_yellow.png";
    }
    if (hp > 50) {
        return "../../static/other/health_bar_green.png";
    }
}

// Name label helper
function getNameToDisplay(objData) {
    if (objData.is_alive) {
        if (objData.player_name) {
            return "🙋‍♂️" + objData.player_name;
        } else if (objData.family_name) {
            return "🧠" + objData.family_name + " " + objData.index;
        }
    }
    return "";
}

// Coordinate interpolation helper
function interpolatePosition(obj, playerObj, timeDelta, screenWidth, screenHeight) {
    const maxDim = Math.max(screenWidth, screenHeight);
    const playerObjX = (((playerObj.x_new - playerObj.x) * timeDelta) + playerObj.x) / 20 * maxDim;
    const playerObjY = (((playerObj.y_new - playerObj.y) * timeDelta) + playerObj.y) / 20 * maxDim;

    const spriteX = (((obj.x_new - obj.x) * timeDelta) + obj.x) / 20 * maxDim - playerObjX + screenWidth / 2;
    const spriteY = (((obj.y_new - obj.y) * timeDelta) + obj.y) / 20 * maxDim - playerObjY + screenHeight / 2;
    const spriteAngle = ((((obj.rotation_new - obj.rotation) * timeDelta) + obj.rotation) - 1) * 90.0;

    return { x: spriteX, y: spriteY, angle: spriteAngle };
}

// Particle alpha / scaling helper
function computeParticleProperties(objData, screenWidth, screenHeight) {
    const lifeRatio = objData.life / objData.lifetime;
    const alpha = 1 - lifeRatio;
    let y_new = objData.y;
    let height_new = null;
    let width_new = null;
    const maxDim = Math.max(screenWidth, screenHeight);

    if (objData.motion === 'up') {
        y_new = objData.y - lifeRatio;
    }
    if (objData.motion === 'scale') {
        height_new = lifeRatio * 15 * (1 / 20.0) * maxDim;
        width_new = lifeRatio * 15 * (1 / 20.0) * maxDim;
    }
    return { alpha, y_new, height_new, width_new };
}

describe('Frontend Game Client Logic', () => {
    describe('Health Bar Color Thresholds', () => {
        test('critical health (hp <= 20) uses red bar', () => {
            assert.strictEqual(getHealthBarTexture(10), "../../static/other/health_bar_red.png");
            assert.strictEqual(getHealthBarTexture(20), "../../static/other/health_bar_red.png");
        });

        test('medium health (20 < hp <= 50) uses yellow bar', () => {
            assert.strictEqual(getHealthBarTexture(21), "../../static/other/health_bar_yellow.png");
            assert.strictEqual(getHealthBarTexture(50), "../../static/other/health_bar_yellow.png");
        });

        test('high health (hp > 50) uses green bar', () => {
            assert.strictEqual(getHealthBarTexture(51), "../../static/other/health_bar_green.png");
            assert.strictEqual(getHealthBarTexture(100), "../../static/other/health_bar_green.png");
        });
    });

    describe('Name Tag Display Formatting', () => {
        test('player object shows user icon and username', () => {
            const data = { is_alive: true, player_name: "Alice", family_name: "default", index: 1 };
            assert.strictEqual(getNameToDisplay(data), "🙋‍♂️Alice");
        });

        test('bot object shows brain icon, family name, and index', () => {
            const data = { is_alive: true, player_name: null, family_name: "AlphaTeam", index: 42 };
            assert.strictEqual(getNameToDisplay(data), "🧠AlphaTeam 42");
        });

        test('wild/dead object has no name tag', () => {
            const deadPlayer = { is_alive: false, player_name: "Alice", index: 1 };
            assert.strictEqual(getNameToDisplay(deadPlayer), "");

            const wildAnimal = { is_alive: true, player_name: null, family_name: null, index: 2 };
            assert.strictEqual(getNameToDisplay(wildAnimal), "");
        });
    });

    describe('Position & Angle Interpolation', () => {
        test('player at center of screen', () => {
            const player = { x: 5, x_new: 5, y: 5, y_new: 5 };
            const result = interpolatePosition(player, player, 0.5, 800, 600);
            assert.strictEqual(result.x, 400); // 800 / 2
            assert.strictEqual(result.y, 300); // 600 / 2
        });

        test('rotation to angle conversion', () => {
            // Rotations: UP=1 -> 0 deg, RIGHT=2 -> 90 deg, DOWN=3 -> 180 deg, LEFT=4 -> 270 deg
            const player = { x: 0, x_new: 0, y: 0, y_new: 0 };
            
            const upObj = { x: 0, x_new: 0, y: 0, y_new: 0, rotation: 1, rotation_new: 1 };
            assert.strictEqual(interpolatePosition(upObj, player, 0, 800, 600).angle, 0);

            const rightObj = { x: 0, x_new: 0, y: 0, y_new: 0, rotation: 2, rotation_new: 2 };
            assert.strictEqual(interpolatePosition(rightObj, player, 0, 800, 600).angle, 90);

            const downObj = { x: 0, x_new: 0, y: 0, y_new: 0, rotation: 3, rotation_new: 3 };
            assert.strictEqual(interpolatePosition(downObj, player, 0, 800, 600).angle, 180);

            const leftObj = { x: 0, x_new: 0, y: 0, y_new: 0, rotation: 4, rotation_new: 4 };
            assert.strictEqual(interpolatePosition(leftObj, player, 0, 800, 600).angle, 270);
        });
    });

    describe('Particle Computations', () => {
        test('fades alpha linearly with life', () => {
            const particleData = { x: 5, y: 5, life: 5, lifetime: 10, motion: 'up' };
            const res = computeParticleProperties(particleData, 800, 600);
            assert.strictEqual(res.alpha, 0.5);
            assert.strictEqual(res.y_new, 4.5);
        });

        test('scale motion expands with life ratio', () => {
            const particleData = { x: 5, y: 5, life: 10, lifetime: 10, motion: 'scale' };
            const res = computeParticleProperties(particleData, 1000, 1000);
            assert.strictEqual(res.alpha, 0.0);
            assert.strictEqual(res.height_new, 1.0 * 15 * 0.05 * 1000); // 750
        });
    });

    describe('Keyboard Input State Tracking', () => {
        test('logKey, clearKey, clear_keys tracking', () => {
            let keys_pressed = {
                ArrowRight: false,
                ArrowLeft: false,
                ArrowDown: false,
                ArrowUp: false,
            };

            function logKey(code) {
                if (keys_pressed.hasOwnProperty(code)) {
                    keys_pressed[code] = true;
                }
            }

            function clearKey(code) {
                if (keys_pressed.hasOwnProperty(code)) {
                    keys_pressed[code] = false;
                }
            }

            logKey("ArrowUp");
            assert.strictEqual(keys_pressed.ArrowUp, true);
            assert.strictEqual(keys_pressed.ArrowDown, false);

            logKey("ArrowRight");
            assert.strictEqual(keys_pressed.ArrowRight, true);

            clearKey("ArrowUp");
            assert.strictEqual(keys_pressed.ArrowUp, false);
            assert.strictEqual(keys_pressed.ArrowRight, true);

            // clear all
            keys_pressed = { ArrowRight: false, ArrowLeft: false, ArrowDown: false, ArrowUp: false };
            assert.strictEqual(keys_pressed.ArrowRight, false);
        });
    });
});
