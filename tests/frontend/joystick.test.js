const { test, describe } = require('node:test');
const assert = require('node:assert');

// Pure calculation implementation matching play.html joystick_to_keys
function joystickToKeys(dragtarget, screenWidth, screenHeight) {
    const keys_pressed = {
        ArrowRight: false,
        ArrowLeft: false,
        ArrowDown: false,
        ArrowUp: false
    };

    const x_diff = dragtarget.x - screenWidth / 2;
    const y_diff = dragtarget.y - screenHeight * 0.8;

    const angle = (Math.atan2(x_diff, y_diff) / 3.14) * 180;
    const dist = Math.sqrt(x_diff * x_diff + y_diff * y_diff);

    if (dist > 5) {
        if ((angle > (90 - 45)) && (angle <= (90 + 45))) {
            keys_pressed.ArrowRight = true;
        }
        if ((angle > (180 - 45)) && (angle <= (180 + 45))) {
            keys_pressed.ArrowUp = true;
        }
        if ((angle > (-90 - 45)) && (angle <= (-90 + 45))) {
            keys_pressed.ArrowLeft = true;
        }
        if ((angle > (0 - 45)) && (angle <= (0 + 45))) {
            keys_pressed.ArrowDown = true;
        }
    }

    return { keys: keys_pressed, angle, dist };
}

describe('Frontend Joystick Logic', () => {
    const screenWidth = 1000;
    const screenHeight = 800;
    const centerX = screenWidth / 2; // 500
    const centerY = screenHeight * 0.8; // 640

    test('deadzone: dist <= 5 results in no keys pressed', () => {
        const result = joystickToKeys({ x: centerX + 2, y: centerY + 2 }, screenWidth, screenHeight);
        assert.strictEqual(result.keys.ArrowRight, false);
        assert.strictEqual(result.keys.ArrowLeft, false);
        assert.strictEqual(result.keys.ArrowUp, false);
        assert.strictEqual(result.keys.ArrowDown, false);
    });

    test('drag right triggers ArrowRight', () => {
        // x positive, y zero -> angle approx 90
        const result = joystickToKeys({ x: centerX + 50, y: centerY }, screenWidth, screenHeight);
        assert.strictEqual(result.keys.ArrowRight, true);
        assert.strictEqual(result.keys.ArrowLeft, false);
        assert.strictEqual(result.keys.ArrowUp, false);
        assert.strictEqual(result.keys.ArrowDown, false);
    });

    test('drag left triggers ArrowLeft', () => {
        // x negative, y zero -> angle approx -90
        const result = joystickToKeys({ x: centerX - 50, y: centerY }, screenWidth, screenHeight);
        assert.strictEqual(result.keys.ArrowLeft, true);
        assert.strictEqual(result.keys.ArrowRight, false);
        assert.strictEqual(result.keys.ArrowUp, false);
        assert.strictEqual(result.keys.ArrowDown, false);
    });

    test('drag down triggers ArrowDown', () => {
        // x zero, y positive -> angle approx 0
        const result = joystickToKeys({ x: centerX, y: centerY + 50 }, screenWidth, screenHeight);
        assert.strictEqual(result.keys.ArrowDown, true);
        assert.strictEqual(result.keys.ArrowUp, false);
        assert.strictEqual(result.keys.ArrowLeft, false);
        assert.strictEqual(result.keys.ArrowRight, false);
    });

    test('drag up triggers ArrowUp', () => {
        // x zero, y negative -> angle approx 180 / -180
        const result = joystickToKeys({ x: centerX + 1, y: centerY - 50 }, screenWidth, screenHeight);
        assert.strictEqual(result.keys.ArrowUp, true);
        assert.strictEqual(result.keys.ArrowDown, false);
        assert.strictEqual(result.keys.ArrowLeft, false);
        assert.strictEqual(result.keys.ArrowRight, false);
    });
});
