import { BrewTagShell } from "@/components/brew/BrewTagShell";
import { BrewTagHome } from "@/components/landing/BrewTagHome";

export default function Home() {
  return (
    <BrewTagShell>
      <BrewTagHome />
    </BrewTagShell>
  );
}
