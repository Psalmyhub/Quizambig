import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

export const QUIZAMBIG_CONTRACT_ADDRESS = "0xC57Ac7ACF54bB4D4761Ff7150F455E190cc113E3" as const;
export const QUIZAMBIG_OWNER = "0xB41f7CcF919515a4741C7AAd43cFfCd56A20Ee31" as const;

type EthereumProvider = {
  request(args: { method: string; params?: unknown[] }): Promise<unknown>;
};

declare global {
  interface Window { ethereum?: EthereumProvider; }
}

export type Quiz = {
  id:number; master:string; title:string; description:string; question_count:number;
  overall_duration_seconds:number; created_at:number; published_at:number; expires_at:number; status:string;
};
export type Question = {
  id:number; quiz_id:string; question_text:string; answer_length:number; answer_mode:"TEXT"|"NUMERIC";
  automatic_time:number; custom_time:number; has_custom_time:boolean; final_time:number;
  start_time:number; deadline:number; status:string; answer_revealed:boolean;
};
export type Evaluation = {
  question_id:number; player:string; status:string; semantic_score:number; correct:boolean;
};

const readClient = () => createClient({ chain: studionet });

async function walletAddress(): Promise<`0x${string}`> {
  if (!window.ethereum) throw new Error("No browser wallet detected.");
  const accounts = await window.ethereum.request({method:"eth_requestAccounts"});
  const address = Array.isArray(accounts) ? accounts[0] : undefined;
  if (typeof address !== "string") throw new Error("No wallet account returned.");
  return address as `0x${string}`;
}

function writeClient(account:`0x${string}`) {
  if (!window.ethereum) throw new Error("No browser wallet detected.");
  return createClient({chain:studionet, account, provider:window.ethereum});
}

export const connectWallet = walletAddress;

export async function getNextQuizId() {
  return Number(await readClient().readContract({address:QUIZAMBIG_CONTRACT_ADDRESS,functionName:"get_next_quiz_id",args:[]}));
}
export async function getQuiz(id:number):Promise<Quiz> {
  return await readClient().readContract({address:QUIZAMBIG_CONTRACT_ADDRESS,functionName:"get_quiz",args:[id],jsonSafeReturn:true}) as Quiz;
}
export async function getQuestion(id:number):Promise<Question> {
  return await readClient().readContract({address:QUIZAMBIG_CONTRACT_ADDRESS,functionName:"get_question",args:[id],jsonSafeReturn:true}) as Question;
}
export async function getPlayerStatus(id:number,player:`0x${string}`) {
  return await readClient().readContract({address:QUIZAMBIG_CONTRACT_ADDRESS,functionName:"get_player_status",args:[id,player],jsonSafeReturn:true}) as {joined:boolean;quiz_id:number;player:string};
}
export async function getEvaluation(questionId:number,player:`0x${string}`) {
  return await readClient().readContract({address:QUIZAMBIG_CONTRACT_ADDRESS,functionName:"get_evaluation",args:[questionId,player],jsonSafeReturn:true}) as Evaluation;
}
async function write(functionName:string,args:unknown[]) {
  const account=await walletAddress();
  const client=writeClient(account);
  const call={address:QUIZAMBIG_CONTRACT_ADDRESS,functionName,args};
  const estimate=await client.estimateTransactionFeesForWrite(call);
  const hash=await client.writeContract({...call,fees:{distribution:estimate.distribution,feeValue:estimate.feeValue}});
  await client.waitForDecision({hash});
  return hash;
}
export const joinQuiz=(id:number)=>write("join_quiz",[id]);
export const submitAnswer=(questionId:number,answer:string)=>write("submit_answer",[questionId,answer]);
export const startQuestion=(questionId:number)=>write("start_question",[questionId]);
export const closeQuestion=(questionId:number)=>write("close_question",[questionId]);
export const revealMasterAnswer=(questionId:number,answer:string,salt:string)=>write("reveal_master_answer",[questionId,answer,salt]);
export const evaluateSubmission=(questionId:number,player:`0x${string}`)=>write("evaluate_submission",[questionId,player]);
