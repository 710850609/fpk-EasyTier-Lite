<template>
  <div ref="editorRef" class="code-editor"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, keymap, lineNumbers } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { oneDark } from '@codemirror/theme-one-dark'
import { defaultKeymap, indentWithTab } from '@codemirror/commands'
import { syntaxHighlighting, defaultHighlightStyle, StreamLanguage } from '@codemirror/language'
import { toml } from '@codemirror/legacy-modes/mode/toml'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'toml'
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
let editorView = null

// TOML 语言支持
const tomlLanguage = StreamLanguage.define(toml)

onMounted(() => {
  if (!editorRef.value) return

  const startState = EditorState.create({
    doc: props.modelValue,
    extensions: [
      lineNumbers(),
      oneDark,
      tomlLanguage,
      keymap.of([...defaultKeymap, indentWithTab]),
      syntaxHighlighting(defaultHighlightStyle),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          emit('update:modelValue', update.state.doc.toString())
        }
      }),
      EditorView.theme({
        '&': {
          fontSize: '14px',
          fontFamily: '"Fira Code", "JetBrains Mono", Consolas, Monaco, monospace'
        },
        '.cm-editor': {
          height: '100%',
          maxHeight: '100%'
        },
        '.cm-scroller': {
          overflow: 'auto'
        },
        '.cm-content': {
          padding: '16px',
          lineHeight: '1.7'
        },
        '.cm-gutters': {
          backgroundColor: '#0d1117',
          borderRight: '1px solid #30363d',
          paddingLeft: '8px',
          paddingRight: '8px'
        },
        '.cm-lineNumbers': {
          color: '#484f58'
        },
        '.cm-activeLineGutter': {
          backgroundColor: '#21262d'
        },
        '.cm-activeLine': {
          backgroundColor: 'rgba(56, 139, 253, 0.1)'
        },
        '.cm-selectionBackground': {
          backgroundColor: 'rgba(56, 139, 253, 0.3) !important'
        },
        '.cm-cursor': {
          borderLeftColor: '#58a6ff'
        },
        '&.cm-focused': {
          outline: 'none'
        }
      }),
      EditorView.editorAttributes.of({
        style: 'height: 100%'
      }),
      EditorState.readOnly.of(props.readonly)
    ]
  })

  editorView = new EditorView({
    state: startState,
    parent: editorRef.value
  })

  // 使用 ResizeObserver 确保编辑器正确适应容器
  const resizeObserver = new ResizeObserver(() => {
    if (editorView) {
      editorView.requestMeasure()
    }
  })
  resizeObserver.observe(editorRef.value)

  // 保存引用以便清理
  editorRef.value._resizeObserver = resizeObserver
})

onUnmounted(() => {
  if (editorRef.value && editorRef.value._resizeObserver) {
    editorRef.value._resizeObserver.disconnect()
  }
  if (editorView) {
    editorView.destroy()
  }
})

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  if (editorView && newValue !== editorView.state.doc.toString()) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: newValue
      }
    })
  }
})
</script>

<style scoped>
.code-editor {
  height: 100%;
  width: 100%;
}

:deep(.cm-editor) {
  height: 100%;
}

:deep(.cm-scroller) {
  overflow: auto;
}

/* TOML 语法高亮样式 */
:deep(.cm-keyword) { color: #ff7b72; }      /* 关键字如 true/false */
:deep(.cm-string) { color: #a5d6ff; }      /* 字符串 */
:deep(.cm-number) { color: #79c0ff; }      /* 数字 */
:deep(.cm-comment) { color: #8b949e; font-style: italic; }  /* 注释 */
:deep(.cm-property) { color: #7ee787; }    /* 属性名/键名 */
:deep(.cm-operator) { color: #ff7b72; }    /* 操作符如 = */
:deep(.cm-punctuation) { color: #c9d1d9; } /* 标点符号 */

/* 滚动条样式 */
:deep(.cm-scroller::-webkit-scrollbar) {
  width: 12px;
  height: 12px;
}

:deep(.cm-scroller::-webkit-scrollbar-track) {
  background: #0d1117;
}

:deep(.cm-scroller::-webkit-scrollbar-thumb) {
  background: #30363d;
  border-radius: 6px;
  border: 3px solid #0d1117;
}

:deep(.cm-scroller::-webkit-scrollbar-thumb:hover) {
  background: #484f58;
}
</style>
