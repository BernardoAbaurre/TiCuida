<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import iconeEditar from '../assets/figma/editar.svg'
import AvisoLegal from '../components/AvisoLegal.vue'
import BarraEtapas from '../components/BarraEtapas.vue'
import ErrosCampo from '../components/ErrosCampo.vue'
import api, { errosDeCampo, mensagemErro } from '../services/api'
import { sessao } from '../stores/sessao'
import { INICIOS_SINTOMAS, formatarTelefone, rotuloInicio } from '../utils/formatos'

const router = useRouter()
const TOTAL_ETAPAS = 4

const etapa = ref(1)
const sintomas = ref([])
const carregando = ref(true)
const enviando = ref(false)
const erroGeral = ref('')
const erros = ref({})

const form = reactive({
  queixa_principal: '',
  comuns: [],
  alarmes: [],
  intensidade: 0,
  inicio_sintomas: '',
  mediuTemperatura: false,
  temperatura: '',
})

const sintomasComuns = computed(() => sintomas.value.filter((s) => !s.sinal_alarme))
const sinaisAlarme = computed(() => sintomas.value.filter((s) => s.sinal_alarme))
const temAlarme = computed(() => form.alarmes.length > 0)
const paciente = computed(() => sessao.usuario?.paciente)
const nomesSelecionados = computed(() =>
  sintomas.value.filter((s) => [...form.comuns, ...form.alarmes].includes(s.id)).map((s) => s.nome),
)

// Em qual etapa cada campo aparece, para voltar até ela se a API apontar erro
const ETAPA_DO_CAMPO = { queixa_principal: 1, sintomas: 1, intensidade: 3, inicio_sintomas: 3, temperatura: 3 }

onMounted(async () => {
  try {
    sintomas.value = (await api.get('/sintomas')).data
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
})

function validarEtapa(n) {
  const e = {}
  if (n === 1 && form.queixa_principal.trim().length < 3)
    e.queixa_principal = ['Descreva em poucas palavras o que você está sentindo.']
  if (n === 3) {
    if (!form.inicio_sintomas) e.inicio_sintomas = ['Informe há quanto tempo começou.']
    if (form.mediuTemperatura) {
      const t = Number(form.temperatura)
      if (!form.temperatura || Number.isNaN(t) || t < 34 || t > 43)
        e.temperatura = ['Informe a temperatura entre 34 e 43 °C.']
    }
  }
  erros.value = e
  return Object.keys(e).length === 0
}

function avancar() {
  if (!validarEtapa(etapa.value)) return
  // Sinal de alarme interrompe o fluxo: registra a triagem e mostra a orientação do 192
  if (etapa.value === 2 && temAlarme.value) return enviar()
  etapa.value += 1
}

function voltar() {
  erros.value = {}
  etapa.value -= 1
}

async function enviar() {
  erroGeral.value = ''
  enviando.value = true
  try {
    const { data } = await api.post('/triagens', {
      queixa_principal: form.queixa_principal,
      sintomas: [...form.comuns, ...form.alarmes],
      intensidade: Number(form.intensidade),
      inicio_sintomas: form.inicio_sintomas || 'menos_24h',
      temperatura: form.mediuTemperatura ? Number(form.temperatura) : null,
    })
    router.push({
      path: `/triagem/${data.triagem.id}`,
      state: { motivos: [...data.motivos] },
    })
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
    erros.value = errosDeCampo(erro)
    const etapas = Object.keys(erros.value).map((c) => ETAPA_DO_CAMPO[c]).filter(Boolean)
    if (etapas.length) etapa.value = Math.min(...etapas)
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <section class="secao">
    <div class="container" style="max-width: 640px">
      <BarraEtapas :total="TOTAL_ETAPAS" :atual="etapa" @voltar="etapa > 1 ? voltar() : router.back()" />
      <AvisoLegal />

      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>
      <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>

      <form v-else novalidate @submit.prevent="etapa < TOTAL_ETAPAS ? avancar() : enviar()">
        <!-- Etapa 1: sintomas comuns e queixa principal -->
        <div v-show="etapa === 1">
          <h1 class="titulo-pagina">O que você está sentindo?</h1>
          <fieldset class="cartao">
            <legend class="cartao-titulo" style="width: 100%; float: left">Sintomas comuns</legend>
            <div class="lista-checks" style="clear: both">
              <label v-for="s in sintomasComuns" :key="s.id" class="item-check">
                <span>
                  <span class="nome is-block">{{ s.nome }}</span>
                  <span v-if="s.descricao" class="detalhe is-block">{{ s.descricao }}</span>
                </span>
                <input v-model="form.comuns" type="checkbox" :value="s.id" />
              </label>
            </div>
            <ErrosCampo :mensagens="erros.sintomas" />
          </fieldset>

          <div class="caixa-texto">
            <label class="is-sr-only" for="queixa">Descreva o que você está sentindo</label>
            <textarea
              id="queixa"
              v-model="form.queixa_principal"
              :class="{ 'is-danger': erros.queixa_principal }"
              maxlength="500"
              placeholder="Descreva o que você está sentindo. Está sentindo mais algum sintoma?"
            ></textarea>
            <img :src="iconeEditar" alt="" />
          </div>
          <ErrosCampo :mensagens="erros.queixa_principal" />
        </div>

        <!-- Etapa 2: sinais de alarme -->
        <div v-show="etapa === 2">
          <h1 class="titulo-pagina">Você está com algum destes sinais agora?</h1>
          <fieldset class="cartao alarme">
            <legend class="cartao-titulo" style="width: 100%; float: left">Sinais de alarme</legend>
            <p class="texto-pequeno has-text-centered mb-2" style="clear: both">
              Se sim, marque. Eles indicam emergência.
            </p>
            <div class="lista-checks">
              <label v-for="s in sinaisAlarme" :key="s.id" class="item-check">
                <span>
                  <span class="nome is-block">{{ s.nome }}</span>
                  <span v-if="s.descricao" class="detalhe is-block">{{ s.descricao }}</span>
                </span>
                <input v-model="form.alarmes" type="checkbox" :value="s.id" />
              </label>
            </div>
          </fieldset>
          <div v-if="temAlarme" class="notification is-danger is-light" role="alert">
            Você marcou um sinal de alarme. Ao continuar, vamos orientar você a ligar para o
            <strong>192</strong>.
          </div>
        </div>

        <!-- Etapa 3: intensidade, início e temperatura -->
        <div v-show="etapa === 3">
          <h1 class="titulo-pagina">Conte um pouco mais</h1>
          <div class="cartao">
            <label class="cartao-titulo is-block" for="intensidade">Intensidade</label>
            <p class="has-text-centered mb-2">
              Desconforto ou dor: <strong class="has-text-primary">{{ form.intensidade }}</strong> de 10
            </p>
            <input
              id="intensidade"
              v-model.number="form.intensidade"
              class="escala-intensidade"
              type="range"
              min="0"
              max="10"
              step="1"
            />
            <div class="is-flex is-justify-content-space-between texto-pequeno has-text-grey">
              <span>0 – nenhum</span><span>5 – moderado</span><span>10 – insuportável</span>
            </div>
          </div>

          <fieldset class="cartao">
            <legend class="cartao-titulo" style="width: 100%; float: left">Há quanto tempo começou?</legend>
            <div class="lista-checks" style="clear: both">
              <label v-for="i in INICIOS_SINTOMAS" :key="i.valor" class="item-check">
                <span class="nome">{{ i.rotulo }}</span>
                <input v-model="form.inicio_sintomas" type="radio" name="inicio" :value="i.valor" />
              </label>
            </div>
            <ErrosCampo :mensagens="erros.inicio_sintomas" />
          </fieldset>

          <div class="cartao">
            <label class="item-check">
              <span class="nome">Medi minha temperatura</span>
              <input v-model="form.mediuTemperatura" type="checkbox" />
            </label>
            <div v-if="form.mediuTemperatura" class="field mt-2">
              <label class="rotulo" for="temperatura">Temperatura (°C)</label>
              <input
                id="temperatura"
                v-model="form.temperatura"
                class="input campo campo-curto"
                :class="{ 'is-danger': erros.temperatura }"
                type="number"
                inputmode="decimal"
                step="0.1"
                min="34"
                max="43"
                placeholder="Ex.: 38.5"
              />
              <ErrosCampo :mensagens="erros.temperatura" />
            </div>
          </div>
        </div>

        <!-- Etapa 4: confirmação -->
        <div v-show="etapa === 4">
          <h1 class="titulo-pagina">Confirmação de dados</h1>
          <div class="cartao">
            <h2 class="cartao-titulo">O que você está sentindo</h2>
            <table class="tabela-dados">
              <tbody>
                <tr><th>Queixa</th><td>{{ form.queixa_principal }}</td></tr>
                <tr><th>Sintomas</th><td>{{ nomesSelecionados.join(', ') || 'Nenhum marcado' }}</td></tr>
                <tr><th>Intensidade</th><td>{{ form.intensidade }} de 10</td></tr>
                <tr><th>Início</th><td>{{ rotuloInicio(form.inicio_sintomas) }}</td></tr>
                <tr>
                  <th>Temperatura</th>
                  <td>{{ form.mediuTemperatura ? `${form.temperatura} °C` : 'Não medida' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="cartao">
            <h2 class="cartao-titulo">Dados de identificação</h2>
            <table v-if="paciente" class="tabela-dados">
              <tbody>
                <tr><th>Nome</th><td>{{ paciente.nome }}</td></tr>
                <tr><th>Idade</th><td>{{ paciente.idade }} anos</td></tr>
                <tr><th>Convênio</th><td>{{ paciente.convenio?.nome }}</td></tr>
                <tr><th>Telefone</th><td>{{ formatarTelefone(paciente.telefone) }}</td></tr>
              </tbody>
            </table>
            <p class="texto-pequeno has-text-grey mt-3">
              Dados desatualizados? <RouterLink to="/perfil">Edite seu perfil</RouterLink>.
            </p>
          </div>
        </div>

        <div class="acoes-form">
          <button
            class="button botao"
            :class="[{ 'is-perigo': etapa === 2 && temAlarme }, { 'is-loading': enviando }]"
            type="submit"
          >
            <template v-if="etapa === 2 && temAlarme">Ver orientação</template>
            <template v-else-if="etapa < TOTAL_ETAPAS">Próximo</template>
            <template v-else>Enviar</template>
          </button>
        </div>
      </form>
    </div>
  </section>
</template>
