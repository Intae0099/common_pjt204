import { h, render } from "vue"
import BaseAlert from "@/components/BaseAlert.vue"

export function showConfirm(message, { showCancel = true } = {}) {
  return new Promise((resolve) => {
    const container = document.createElement("div")
    document.body.appendChild(container)

    const vnode = h(BaseAlert, {
      message,
      showCancel,
      onConfirm: () => {
        cleanup()
        resolve(true)
      },
      onCancel: () => {
        cleanup()
        resolve(false)
      }
    })

    function cleanup() {
      render(null, container)
      document.body.removeChild(container)
    }

    render(vnode, container)
  })
}
