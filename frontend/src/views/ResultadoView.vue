<script setup>
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import iconeCaminhada from '../assets/figma/caminhada.svg'
import iconeCarro from '../assets/figma/carro.svg'
import chevron from '../assets/figma/chevron.svg'
import setaVoltar from '../assets/figma/seta-voltar.svg'
import AlertaEmergencia from '../components/AlertaEmergencia.vue'
import AvisoLegal from '../components/AvisoLegal.vue'
import TagPrioridade from '../components/TagPrioridade.vue'
import api, { mensagemErro } from '../services/api'
import { sessao } from '../stores/sessao'
import { LOTACAO, TIPOS_UNIDADE, formatarTelefone, linkRota, tempoRelativo } from '../utils/formatos'

const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()

// Centro padrão do mapa (Vila Velha – ES) quando não há localização nem unidades
const CENTRO_PADRAO = [-20.3297, -40.2925]

const triagem = ref(null)
const motivos = ref(window.history.state?.motivos ?? [])
const unidades = ref([])
const localizacao = ref('pendente') // pendente | ok | negada | indisponivel
const posicao = ref(null)
const carregando = ref(true)
const carregandoUnidades = ref(false)
const erroGeral = ref('')
const escolhida = ref(null)
const enviando = ref(false)
const ordenacao = ref('lotacao') // lotacao (ordem da API) | distancia
const expandida = ref(null)
const mapaEl = ref(null)
let mapa = null
let camadaMarcadores = null

const emergencia = computed(() => triagem.value?.prioridade === 'emergencia')
const convenio = computed(() => sessao.usuario?.paciente?.convenio?.nome)

const unidadesOrdenadas = computed(() => {
  if (ordenacao.value !== 'distancia') return unidades.value
  return [...unidades.value].sort(
    (a, b) => (a.distancia_km ?? Infinity) - (b.distancia_km ?? Infinity),
  )
})

onMounted(async () => {
  try {
    triagem.value = (await api.get(`/triagens/${props.id}`)).data
    if (triagem.value.encaminhamento_id) {
      router.replace(`/protocolo/${triagem.value.encaminhamento_id}`)
      return
    }
    if (!emergencia.value) buscarComLocalizacao()
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
})

onBeforeUnmount(() => {
  if (mapa) mapa.remove()
})

function buscarComLocalizacao() {
  if (!('geolocation' in navigator)) {
    localizacao.value = 'indisponivel'
    return carregarUnidades()
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      localizacao.value = 'ok'
      posicao.value = [pos.coords.latitude, pos.coords.longitude]
      carregarUnidades(pos.coords.latitude, pos.coords.longitude)
    },
    () => {
      localizacao.value = 'negada'
      carregarUnidades()
    },
    { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
  )
}

async function carregarUnidades(lat, lng) {
  carregandoUnidades.value = true
  try {
    const params = lat != null ? { lat: lat.toFixed(6), lng: lng.toFixed(6) } : {}
    unidades.value = (await api.get('/unidades', { params })).data.unidades
    expandida.value = unidades.value[0]?.id ?? null
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregandoUnidades.value = false
  }
}

// ---------- Mapa (Leaflet + OpenStreetMap) ----------
function iconeMarcador(classe) {
  return L.divIcon({ className: '', html: `<span class="marcador ${classe}"></span>`, iconSize: [26, 26] })
}

function desenharMapa() {
  if (!mapaEl.value) return
  if (!mapa) {
    mapa = L.map(mapaEl.value, { zoomControl: false, scrollWheelZoom: false }).setView(CENTRO_PADRAO, 13)
    L.control.zoom({ position: 'bottomleft' }).addTo(mapa)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap',
    }).addTo(mapa)
    camadaMarcadores = L.layerGroup().addTo(mapa)
  }
  camadaMarcadores.clearLayers()
  const pontos = []
  for (const u of unidades.value) {
    const ponto = [u.latitude, u.longitude]
    pontos.push(ponto)
    L.marker(ponto, { icon: iconeMarcador(u.id === expandida.value ? 'ativo' : ''), title: u.nome })
      .on('click', () => focarUnidade(u.id))
      .addTo(camadaMarcadores)
  }
  if (posicao.value) {
    pontos.push(posicao.value)
    L.marker(posicao.value, { icon: iconeMarcador('voce'), title: 'Você' }).addTo(camadaMarcadores)
  }
  if (pontos.length) mapa.fitBounds(pontos, { padding: [40, 40], maxZoom: 15 })
}

watch([unidades, expandida, mapaEl], () => nextTick(desenharMapa))

function focarUnidade(id) {
  expandida.value = id
  nextTick(() => document.getElementById(`unidade-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' }))
}

function alternar(id) {
  expandida.value = expandida.value === id ? null : id
}

// ---------- Apresentação ----------
const PALAVRAS_IGNORADAS = ['hospital', 'pronto', 'atendimento', 'clinica', 'clínica', 'unidade', 'de', 'da', 'do', 'das', 'dos']

function iniciais(nome) {
  const palavras = nome.split(/\s+/).filter((p) => !PALAVRAS_IGNORADAS.includes(p.toLowerCase()))
  return (palavras.length ? palavras : nome.split(/\s+/))
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')
}

// Estimativa simples: 5 km/h a pé e 30 km/h de carro em área urbana
function minutos(km, velocidade) {
  return Math.max(1, Math.round((km / velocidade) * 60))
}

function horario(u) {
  return u.aberto_24h ? 'Aberto 24 horas' : `${u.horario_abertura} às ${u.horario_fechamento}`
}

async function confirmarIda() {
  enviando.value = true
  erroGeral.value = ''
  try {
    const { data } = await api.post('/encaminhamentos', {
      triagem_id: Number(props.id),
      unidade_id: escolhida.value.id,
    })
    router.push(`/protocolo/${data.id}`)
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
    escolhida.value = null
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <section v-if="carregando || erroGeral || emergencia || !triagem" class="secao">
    <div class="container" style="max-width: 720px">
      <AvisoLegal />
      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>
      <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>
      <AlertaEmergencia v-else-if="emergencia" :orientacao="triagem.orientacao" />
    </div>
  </section>

  <template v-if="triagem && !emergencia">
    <div class="resultado-mapa">
      <div ref="mapaEl" class="mapa" aria-label="Mapa das unidades recomendadas"></div>
      <div class="filtro-mapa">
        <button class="botao-voltar" type="button" aria-label="Voltar" @click="router.push('/meus-atendimentos')">
          <img :src="setaVoltar" alt="" />
        </button>
        <div>
          <p class="rotulo-filtro">Filtrar por:</p>
          <div class="filtro-opcoes" role="group" aria-label="Ordenar unidades">
            <button
              class="pilula"
              :class="{ ativa: ordenacao === 'lotacao' }"
              type="button"
              :aria-pressed="ordenacao === 'lotacao'"
              @click="ordenacao = 'lotacao'"
            >
              ⇅ Lotação
            </button>
            <button
              class="pilula"
              :class="{ ativa: ordenacao === 'distancia' }"
              type="button"
              :aria-pressed="ordenacao === 'distancia'"
              :disabled="localizacao !== 'ok'"
              :title="localizacao !== 'ok' ? 'Permita o acesso à localização para ordenar por distância' : ''"
              @click="ordenacao = 'distancia'"
            >
              ➤ Distância
            </button>
          </div>
        </div>
      </div>
    </div>

    <section class="painel-unidades">
      <div class="puxador" aria-hidden="true"></div>
      <div class="painel-unidades-conteudo">
        <h1>Sua unidade de saúde ideal</h1>

        <div class="cartao-prioridade" :class="`borda-prioridade-${triagem.prioridade}`">
          <p class="texto-pequeno has-text-grey mb-1">Prioridade sugerida</p>
          <TagPrioridade :prioridade="triagem.prioridade" grande />
          <p class="mt-2">{{ triagem.orientacao }}</p>
          <ul v-if="motivos.length" class="texto-pequeno has-text-grey mt-2">
            <li v-for="m in motivos" :key="m">• {{ m }}</li>
          </ul>
          <p class="texto-pequeno has-text-grey mt-2">
            É só uma sugestão: a classificação oficial é feita pela equipe da unidade. Aceitam
            <strong>{{ convenio }}</strong>.
            <template v-if="localizacao === 'negada' || localizacao === 'indisponivel'">
              Sem acesso à sua localização, a distância não é considerada.
              <a href="#" @click.prevent="buscarComLocalizacao">Tentar de novo</a>
            </template>
          </p>
        </div>

        <progress
          v-if="carregandoUnidades || localizacao === 'pendente'"
          class="progress is-small is-primary"
          max="100"
        >
          Buscando unidades
        </progress>
        <div v-else-if="!unidades.length" class="notification is-light">
          Nenhuma unidade cadastrada aceita o seu convênio no momento.
        </div>

        <article v-for="u in unidadesOrdenadas" :id="`unidade-${u.id}`" :key="u.id" class="unidade">
          <div class="unidade-cartao">
            <div class="unidade-corpo">
              <div class="unidade-topo">
                <span class="unidade-logo" aria-hidden="true">{{ iniciais(u.nome) }}</span>
                <div>
                  <h2 class="unidade-nome">{{ u.nome }}</h2>
                  <p class="unidade-endereco">{{ TIPOS_UNIDADE[u.tipo] }} · {{ u.endereco }}</p>
                </div>
              </div>

              <div class="unidade-dados">
                <div>
                  <p class="rotulo-dado">Distância</p>
                  <p v-if="u.distancia_km != null" class="valor-dado distancia">
                    <span title="A pé"><img :src="iconeCaminhada" alt="A pé" />{{ minutos(u.distancia_km, 5) }} min</span>
                    <span title="De carro"><img :src="iconeCarro" alt="De carro" />{{ minutos(u.distancia_km, 30) }} min</span>
                  </p>
                  <p v-else class="valor-dado">—</p>
                </div>
                <div>
                  <p class="rotulo-dado">Lotação</p>
                  <p class="valor-dado">{{ u.lotacao ? LOTACAO[u.lotacao.nivel].curto : 'Não informada' }}</p>
                  <p v-if="u.lotacao" class="valor-dado has-text-grey" style="text-transform: none">
                    {{ tempoRelativo(u.lotacao.atualizado_em) }}
                  </p>
                </div>

                <template v-if="expandida === u.id">
                  <div class="largo">
                    <p class="rotulo-dado">Horário de funcionamento</p>
                    <p class="valor-dado">
                      {{ horario(u) }} ·
                      <span :class="u.aberta_agora ? 'has-text-success' : 'has-text-danger'">
                        {{ u.aberta_agora ? 'aberta agora' : 'fechada agora' }}
                      </span>
                    </p>
                  </div>
                  <div class="largo">
                    <p class="rotulo-dado">Contato</p>
                    <p class="valor-dado">
                      <a v-if="u.telefone" :href="`tel:${u.telefone}`">{{ formatarTelefone(u.telefone) }}</a>
                      <template v-if="u.telefone"> · </template>
                      <a :href="linkRota(u.latitude, u.longitude)" target="_blank" rel="noopener">Ver rota</a>
                      <template v-if="u.distancia_km != null"> · {{ u.distancia_km }} km</template>
                    </p>
                  </div>
                  <div class="largo">
                    <p class="rotulo-dado">Convênios</p>
                    <div class="chips">
                      <span v-for="c in u.convenios" :key="c" class="chip" :class="{ destaque: c === convenio }">
                        {{ c }}
                      </span>
                    </div>
                  </div>
                </template>
              </div>
            </div>
            <button
              class="unidade-expandir"
              :class="{ aberto: expandida === u.id }"
              type="button"
              :aria-expanded="expandida === u.id"
              :aria-label="expandida === u.id ? 'Mostrar menos' : 'Mostrar mais'"
              @click="alternar(u.id)"
            >
              <img :src="chevron" alt="" />
            </button>
          </div>
          <button class="estou-indo" type="button" :disabled="!u.aberta_agora" @click="escolhida = u">
            {{ u.aberta_agora ? 'Estou indo!' : 'Fechada agora' }}
          </button>
        </article>
      </div>
    </section>
  </template>

  <!-- Confirmação do "Estou indo" -->
  <div class="modal" :class="{ 'is-active': escolhida }" role="dialog" aria-modal="true" aria-labelledby="titulo-popup">
    <div class="modal-background" @click="escolhida = null"></div>
    <div v-if="escolhida" class="modal-content" style="width: auto; overflow: visible">
      <div class="popup">
        <p id="titulo-popup" class="popup-titulo">CONFIRMAR?</p>
        <p class="popup-texto">
          Vamos enviar sua pré-triagem para o <strong>{{ escolhida.nome }}</strong>.
        </p>
        <button class="button botao" :class="{ 'is-loading': enviando }" type="button" @click="confirmarIda">
          OK
        </button>
        <p class="mt-3">
          <button class="button botao-texto" type="button" @click="escolhida = null">Cancelar</button>
        </p>
      </div>
    </div>
  </div>
</template>
