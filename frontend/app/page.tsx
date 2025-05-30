import Image from "next/image";
import Navbar from "@/components/navbar";
import Container from "@/components/container";
// fetching the classroom details from "/home" in the fastapbackend

export default function Home() {
  return (
    <div>
      <Navbar />
      <Container />
      Boom
    </div>
  );
}
