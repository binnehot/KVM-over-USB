
const KB_EVT_TYPE_KEYDOWN = 1;
const KB_EVT_TYPE_KEYUP = 2;
const KB_EVT_TYPE_RESET = 3;

const keyRemap = {
  Control: 0XE0,
  Shift: 0XE1,
  Alt: 0XE2,
  Meta: 0XE3,
  Tab: 0X2B,
  CapsLock: 0X39,
  Backspace: 0X2A,
  Enter: 0X28,
  ContextMenu: 0X76,
  Insert: 0X49,
  Delete: 0X4C,
  Home: 0X4A,
  End: 0X4D,
  PageUp: 0X4B,
  PageDown: 0X4E,
  ArrowUp: 0X52,
  ArrowDown: 0X51,
  ArrowLeft: 0X50,
  ArrowRight: 0X4F,
  PrintScreen: 0X46,
  ScrollLock: 0X47,
  Pause: 0X48,
  Escape: 0X29,
  " ": 0X2C,
  "\n": 0X28, // "Enter
  Space: 0X2C,
  "\t": 0X2B,
  "`": 0X35,
  ";": 0X33,
  "'": 0X34,
  "~": 0X35,
  ":": 0X33,
  '"': 0X34,
  "[": 0X2F,
  "]": 0X30,
  "\\": 0X31,
  "{": 0X2F,
  "}": 0X30,
  "|": 0X31,
  "-": 0X2D,
  "_": 0X2D,
  "=": 0X2E,
  "+": 0X2E,
  "1": 0X1E,
  "2": 0X1F,
  "3": 0X20,
  "4": 0X21,
  "5": 0X22,
  "6": 0X23,
  "7": 0X24,
  "8": 0X25,
  "9": 0X26,
  "0": 0X27,
  ")": 0X27,
  "!": 0X1E,
  "@": 0X1F,
  "#": 0X20,
  "$": 0X21,
  "%": 0X22,
  "^": 0X23,
  "&": 0X24,
  "*": 0X25,
  "(": 0X26,
  ",": 0X36,
  ".": 0X37,
  "/": 0X38,
  "<": 0X36,
  ">": 0X37,
  "?": 0X38,
};
const ShiftSymbols = [
  ")", "!", "@", "#", "$", "%",
  "^", "&", "*", "(", "~", "_",
  "+", "{", "}", "|", ":", '"',
  "<", ">", "?",
]
for (let i = 0; i < 12; i += 1) {
  keyRemap[`F${1 + i}`] = 0X3A + i;
}
for (let i = 0; i < 26; i += 1) {
  keyRemap[String.fromCharCode(97 + i)] = 0X04 + i;
}
for (let i = 0; i < 26; i += 1) {
  keyRemap[String.fromCharCode(65 + i)] = 0X04 + i;
}

// console.debug('keyRemap', keyRemap);

export function sendEvent(channel, key, type) {
  // Byte 0: key  - [KeyCode to Press]
  // Byte 1: State  - KB_EVT_TYPE_KEYDOWN | KB_EVT_TYPE_KEYUP | KB_EVT_TYPE_RESET
  let payload = new Array(2);
  payload.fill(0);

  if (type === 'keydown') {
    payload[1] = KB_EVT_TYPE_KEYDOWN;
  } else if (type === 'keyup') {
    payload[1] = KB_EVT_TYPE_KEYUP;
  } else if (type === 'reset') {
    payload[1] = KB_EVT_TYPE_RESET;
  } else {
    return;
  }
  if (type !== 'reset') {
    if (keyRemap[key]) {
      payload[0] = keyRemap[key];
    } else {
      console.warn('Unknown key', key);
      return;
    }
    // console.debug('got payload', payload);
  }

  const msg = {
    type: 'keyboard',
    payload,
  };
  channel.send(JSON.stringify(msg));
  // console.debug('sendEvent', key, type);
}

function sleep(ms = 100) {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

export  function sendSequence(channel, str) {
  let payload = str

  const msg = {
    type: 'paste',
    payload,
  };
  channel.send(JSON.stringify(msg));
}
