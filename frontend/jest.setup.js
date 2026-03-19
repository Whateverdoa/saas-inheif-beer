// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.ResizeObserver = global.ResizeObserver || ResizeObserver

if (typeof global.HTMLElement !== 'undefined' && !global.HTMLElement.prototype.hasPointerCapture) {
  global.HTMLElement.prototype.hasPointerCapture = () => false
}

if (typeof global.Element !== 'undefined' && !global.Element.prototype.scrollIntoView) {
  global.Element.prototype.scrollIntoView = function () {}
}
