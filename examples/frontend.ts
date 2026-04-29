export function canRender(flag: boolean) {
  if (flag) {
    return true;
  }
  return false;
}

export function shouldHide(flag: boolean) {
  return !flag;
}
