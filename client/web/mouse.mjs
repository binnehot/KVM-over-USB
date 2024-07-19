var last_mouse_down_time = 0;
// if up and down are too close, delay the up event 50ms
export function sendEvent(channel, data, type) {
  let payload = new Array(2);
  payload.fill(0);
  if (type === 'move') {
    var type_msg = 'mouse_offset'
    payload[0] = data[0];
    payload[1] = data[1];
  } else if (type === 'abs') {
    var type_msg = 'mouse_pos'
    payload[0] = data[0];
    payload[1] = data[1];
  } else if (type === 'mousedown') {
    var type_msg = 'mouse_btn'
    payload[1] = 2;
    switch (data) {
      case 0:
        payload[0] = 1;
        break;
      case 1:
        payload[0] = 4;
        break;
      case 2:
        payload[0] = 2;
        break;
      case 3:
        payload[0] = 8;
        break;
      case 4:
        payload[0] = 16;
        break;
      default:
        console.warn('Unknown mouse btn', data);
        return;
    }
    last_mouse_down_time = Date.now();
  } else if (type === 'mouseup') {
    var type_msg = 'mouse_btn'
    payload[1] = 3;
    switch (data) {
      case 0:
        payload[0] = 1;
        break;
      case 1:
        payload[0] = 4;
        break;
      case 2:
        payload[0] = 2;
        break;
      case 3:
        payload[0] = 8;
        break;
      case 4:
        payload[0] = 16;
        break;
      default:
        return;
    }
  } else if (type === 'wheel') {
    var type_msg = 'mouse_wheel'
    payload[0] = Math.round(data / 40);
  } else if (type === 'reset') {
    var type_msg = 'mouse_btn'
    payload[1] = 1;
  } else {
    return;
  }

  var msg = {
    type: type_msg,
    payload,
  };
  if (type === 'mouseup' && Date.now() - last_mouse_down_time < 50) {
    setTimeout(function () {
      channel.send(JSON.stringify(msg));
    }, 50);
    console.debug('sendEvent mouse delayed', channel, data, type);
  } else {
    channel.send(JSON.stringify(msg));
  }
  // console.debug('sendEvent mouse', channel, data, type);
}
